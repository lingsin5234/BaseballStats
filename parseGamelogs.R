##############################################################
##                                                          ##
##    Parse Gamelogs                                        ##
##                                                          ##
##    Created by: Sinto Ling                                ##
##    Created on: July 27, 2017                             ##
##                                                          ##
##    Sorts gamelogs into RStudio-friendly tables.          ##
##                                                          ##
##    Version 1.4.0                                         ##
##                                                          ##
##############################################################

################################
##    -- Version History --   ##
################################
##                            
#     1.0.0 - just starting up on this again - July 27, 2017
#     1.0.1 - add the errors - July 27, 2017
#     1.0.2 - parse thru the different plays that occurred. - July 28, 2017
#     1.0.3 - basic hit/K/BB/RBI - August 28, 2017
#     1.0.4 - expand to type of hits - August 28, 2017
#     1.0.5 - added Games Played - August 29, 2017
#     1.0.6 - expanded to track base runners - work in progress still - August 30, 2017
#     1.0.7 - fine tune base runner tracking; need to QA it - September 13, 2017
#     1.0.8 - logic is getting there; notable fixes needed: 
#             Force Outs, Double/Triple Plays - September 14, 2017
#     1.0.9 - FO/FC/DP/TP/CS/PO/SB, multiple steals -- all fixed - September 15, 2017
#     1.1.0 - stolen bases table  - SEPTEMBER 17, 2017
#     1.1.1 - LOB, RISP - September 18, 2017
#     1.1.2 - added "Event" to LOB/RISP; generate intermediate stats tables - September 18, 2017
#     1.1.3 - fixed the column names for Intermediate Stats, ready for export - September 19, 2017
#     1.1.4 - start on pitching stats -- scrapped version
#     1.1.5 - HOME version transferred, fix errors related to Events - September 26, 2017
#     1.1.6 - rewrite the logic using the "." for advances - September 27, 2017
#     1.1.7 - rewrite without big for loops -INFO complete - September 28, 2017
#     1.1.8 - rewrite without big for loops -START complete - September 29, 2017
#     1.1.9 - rewrite without big for loops -PLAYS & SUBS partial - October 3, 2017
#     1.2.0 - rewrite PLAYS portion - October 4, 2017
#     1.2.1 - revised method for PLAYS
#             use play column more, then handle runners and outs - October 5, 2017
#     1.2.2 - clean-up the code a bit - October 6, 2017
#     1.2.3 - thorough error checking - round 1 - October 6, 2017
#     1.2.4 - thorough error checking - round 2 - October 6, 2017
#     1.2.5 - Basic Stats: Hits, Walks, Ks, SBs - October 17, 2017
#     1.2.6 - Basic Stats: HP, CS, SH - October 18, 2017
#     1.2.7 - make a function out of current processing, test <2016 years - October 19, 2017
#           - apply necessary fixes (FO|FC|DP|TP especially) + round 3 testing - October 19, 2017
#     1.3.0 - revampt needed!!! - OCTOBER 20, 2017
#           - first look for the batter runner ONLY (ALL CASES) - October 20, 2017
#     1.3.1 - verify the batter runners reaching base are all dealt with - October 30, 2017
#           - then move the runners (no errors) - October 31, 2017
#     1.3.2 - restyle the method handling Runners code - December 28, 2017
#     1.3.3 - Problem: the order & inclusion of all the different "tags" tg_XX - January 2, 2018
#	1.4.0 - revampt attempt #2 - see "New Plan of Attack" section - JANUARY 3, 2018
#           - bug: search: ## might need more case(s) ## - January 3, 2018
##
################################
################################


################################
##     Libraries & Setup      ##
################################

library(plyr); library(stringr); library(data.table); library(reshape2)
posis <- c("P", "C", "1B", "2B", "3B", "SS", "LF", "CF", "RF", "DH")

###       Getting Help       ###
# library(stringr)
# str_count and str_count_all <- useful for counting within string

################################
################################


################################
##         Functions          ##
################################

# function for comparing vectors while making NAs return FALSE (instead of NA)
compareNA <- function(v1,v2) {
      # This function returns TRUE wherever elements are the same, including NA's,
      # and false everywhere else.
      same <- (v1 == v2)  |  (is.na(v1) & is.na(v2))
      same[is.na(same)] <- FALSE
      return(same)
}

# recursive function to assign outs #
asgn_outs <- function(CLN, all_plyExcp1st, chg_inning) {
      
      # generate a temp table to compare to
      TMP <- CLN
      
      # apply current outs and move to AB_Outs
      CLN$PE_Outs <- CLN$AB_Outs + CLN$Outs
      CLN$AB_Outs[all_plyExcp1st] <- CLN$PE_Outs[all_plyExcp1st-1]
      
      # reset all new inning AB_Outs
      CLN$AB_Outs[chg_inning] <- 0
      
      # compare to tmp table
      if (!isTRUE(all.equal(TMP, CLN))) {
            CLN <- asgn_outs(CLN, all_plyExcp1st, chg_inning)
      }
      return (CLN)
}

# assigning bases based on a single runner information #
asgn_base <- function(CLN, id, rnnr) {

	# check which base the runner came from
	if (grepl("^B", rnnr)) {
		player_id <- CLN$playerID[CLN$ID==id]
	} else if (grepl("^1", rnnr)) {
		player_id <- CLN$AB_1B[CLN$ID==id]
	} else if (grepl("^2", rnnr)) {
		player_id <- CLN$AB_2B[CLN$ID==id]
	} else if (grepl("^3", rnnr)) {
		player_id <- CLN$AB_3B[CLN$ID==id]
	}
	
	# if player_id is NA, ignore for now. 
	# the recursive advance runner script will update in later iteration
	if (is.na(player_id)) {return (CLN)}
	
	# check which base the runner made it to
	if (grepl("1$", rnnr)) {
		CLN$PE_1B[CLN$ID==id] <- player_id
	} else if (grepl("2$", rnnr)) {
		CLN$PE_2B[CLN$ID==id] <- player_id
	} else if (grepl("3$", rnnr)) {
		CLN$PE_3B[CLN$ID==id] <- player_id
	} else if (grepl("H$", rnnr)) {
		CLN$Runs[CLN$ID==id] <- 1
		
		# in case double play but 2 runners scored
		if (grepl("(-H.*-H)|(-H.*XH([1-9]*E[1-9]))|(XH([1-9]*E[1-9]).*XH([1-9]*E[1-9]))", CLN$Runners[CLN$ID==id])) {
			CLN$Runs[CLN$ID==id] <- 2
		}
	}

	return (CLN)
}

################################
################################


################################
##     New Plan of Attack     ##
################################

###    Set Initial States    ###
# 1. Assign all batters getting on base (exclude weird cases + errors)
# 2. Assign all batters getting on base via weird cases + errors
# 3. Calculate all runs and outs during each event

###    Recursive Function    ###
# 1. Assign all runners moving - include errors
# 2. Assign all runners out - include errors
# 3. Assign all runners not moved - include errors
# 4. Transfer runners to next at-bat
# 5. Account for end of inning
# 6. Check for recursive function ending

################################
################################


################################
##   Initial State Function   ##
################################

# function for parsing and creating most basic stats. Export tables in a list!
init_state <- function(EVN, posis) {
      
      # parse headers - this takes a while
      # hdrs <- scan(text = EVN, sep=",", what="", flush=TRUE, quiet=TRUE)
      hdrs <- sapply(strsplit(EVN, ","), "[[", 1) # this faster than scan... like 200 times faster...
      
      # grep line headers
      ID <- grep("id", hdrs)
      info <- grep("info", hdrs)
      strt <- grep("start", hdrs)
      play <- grep("play", hdrs)
      subs <- grep("sub", hdrs)
      dats <- grep("data", hdrs)
      
      # store each game using ID as header ...
      # https://stackoverflow.com/questions/13137490/splitting-a-data-frame-into-a-list-using-intervals
      EVT <- data.frame(EVN, stringsAsFactors=FALSE)
      IDL <- diff(c(ID, length(EVN)+1)) # find the length of each set (game)
      EVT$GRP <- rep(seq_along(ID), IDL) # assign the sets (games)
      
      # split into list of tables
      DF <- split(EVT,EVT[,'GRP'])
      # attach all game ids; simplify=false keeps the list of data frames!!
      DF <- mapply(cbind, DF, as.character(sapply(strsplit(EVT$EVN[grepl("^id", EVT$EVN)], ","), "[[", 2)), SIMPLIFY = FALSE)
      DF <- rbindlist(DF)
      names(DF)[3] <- "ID"
      DF <- DF[,c(3,1)]
      
      # INFO + START
      infoCol <- unique(sapply(strsplit(EVT$EVN[grepl("^info", EVT$EVN)], ","), "[[", 2))
      infoCol <- c("ID", infoCol)
      INFO <- data.frame(matrix(NA, nrow=length(unique(DF$ID)), ncol=length(infoCol)), stringsAsFactors=FALSE)
      names(INFO) <- infoCol
      INFO$ID <- unique(as.character(DF$ID))
      # the following with(DF, tapply) is to transpose each set of "info" with same game ID;
      # converts each list item into data frame and then rbinds list with fill=TRUE - for the "save" column
      # INFO[,2:length(INFO)] <- rbindlist(sapply(with(DF[grepl("^info", DF$EVN),], tapply(EVN, ID, FUN=t)), data.frame), fill=TRUE)[,-1]
      ### above not working...
      TEMP <- rbindlist(sapply(with(DF[grepl("^info", DF$EVN),], tapply(EVN, ID, FUN=t)), function(x) list(data.frame(x, stringsAsFactors = FALSE))), fill=TRUE)
      names(TEMP) <- infoCol[-1] # assign column names for ease of call
      TEMP$save <- sub("\\,$", ",NA", TEMP$save)
      INFO[,2:length(INFO)] <- lapply(TEMP[,1:length(TEMP)], function(x) sub(".*,", "", x))
      
	
	
      ### add the START info ###
      
      # check if AL game or NL game
      # sort two tables for this
      # AL games first
      TEMP <- rbindlist(sapply(with(DF[grepl("^start", DF$EVN) & DF$ID %in% DF$ID[grepl("info,usedh,true", DF$EVN)],], tapply(EVN, ID, FUN=t)), function(x) list(data.frame(x, stringsAsFactors = FALSE))), fill=TRUE)
      ALG <- stack(TEMP)
      ALG$ID <- rep(INFO$ID[INFO$usedh=="true"], length(ALG))
      ALG$ind <- paste(ALG$ID, sub(".*([0,1]),[0-9],([0-9]+)$", "\\1-\\2", ALG$values), sep="_")
      startDEF <- ALG[names(ALG) %in% c("ID", "values")]
      startDEF <- startDEF[,c(2,1)]
      startDEF <- startDEF[!is.na(startDEF$values),]
      startDEF$team <- sub(".*([0,1]),[0-9],([0-9]+)$", "\\1", startDEF$values)
      startDEF$posi <- as.numeric(sub(".*([0,1]),[0-9],([0-9]+)$", "\\2", startDEF$values))
      POSIT <- data.frame(posi=1:10, POS=posis, stringsAsFactors = FALSE)
      startDEF <- merge(startDEF, POSIT, by="posi", all.x=TRUE)
      startDEF <- startDEF[order(startDEF$ID, startDEF$team, startDEF$posi),]
      startDEF$playerID <- sub("start,([a-z0-9\\-]+),.*", "\\1", startDEF$values)
      startDEF <- dcast(startDEF, ID ~ team + POS, value.var="playerID") # row ~ columns, value ... WOW
      names(startDEF) <- sub("^0", "away", sub("^1", "home", names(startDEF)))
      startDEF <- startDEF[c("ID", paste0("away_", posis), paste0("home_", posis))] # reorder columns by name
      AL_DEF <- startDEF
      
      # NL games next
      TEMP <- rbindlist(sapply(with(DF[grepl("^start", DF$EVN) & DF$ID %in% DF$ID[grepl("info,usedh,false", DF$EVN)],], tapply(EVN, ID, FUN=t)), function(x) list(data.frame(x, stringsAsFactors = FALSE))), fill=TRUE)
      NLG <- stack(TEMP)
      NLG$ID <- rep(INFO$ID[INFO$usedh=="false"], length(NLG))
      NLG$ind <- paste(NLG$ID, sub(".*([0,1]),[0-9],([0-9]+)$", "\\1-\\2", NLG$values), sep="_")
      startDEF <- NLG[names(NLG) %in% c("ID", "values")]
      startDEF <- startDEF[,c(2,1)]
      startDEF <- startDEF[!is.na(startDEF$values),]
      startDEF$team <- sub(".*([0,1]),[0-9],([0-9]+)$", "\\1", startDEF$values)
      startDEF$posi <- as.numeric(sub(".*([0,1]),[0-9],([0-9]+)$", "\\2", startDEF$values))
      POSIT <- data.frame(posi=1:10, POS=posis, stringsAsFactors = FALSE)
      startDEF <- merge(startDEF, POSIT, by="posi", all.x=TRUE)
      startDEF <- startDEF[order(startDEF$ID, startDEF$team, startDEF$posi),]
      startDEF$playerID <- sub("start,([a-z0-9\\-]+),.*", "\\1", startDEF$values)
      startDEF <- dcast(startDEF, ID ~ team + POS, value.var="playerID") # row ~ columns, value ... WOW
      names(startDEF) <- sub("^0", "away", sub("^1", "home", names(startDEF)))
      startDEF <- startDEF[c("ID", paste0("away_", posis[-10]), paste0("home_", posis[-10]))] # reorder columns by name
      NL_DEF <- startDEF
      
      # put both defenses together
      startDEF <- rbind.fill(AL_DEF, NL_DEF)
      
      # now for offense - ignore designated pitcher (not in batting - 0)
      TEMP <- rbindlist(sapply(with(DF[grepl("^start", DF$EVN) & !grepl(",0,[1-9]+$", DF$EVN),], tapply(EVN, ID, FUN=t)), function(x) list(data.frame(x, stringsAsFactors = FALSE))), fill=TRUE)
      OFN <- stack(TEMP)
      OFN$ID <- rep(INFO$ID, length(OFN))
      OFN$ind <- paste(OFN$ID, sub(".*,([0-9]),([0-9]+)$", "\\1", OFN$values), sep="_")
      startOFF <- OFN[names(OFN) %in% c("ID", "values")][grepl("_[1-9]$", OFN$ind),]
      startOFF <- startOFF[,c(2,1)] # rearrange columns, ID first
      BatOrd <- rep(1:9, length(INFO$ID))
      startOFF$BatOrd <- BatOrd[order(BatOrd)]
      startOFF$team <- sub(".*([0,1]),[0-9],([0-9]+)$", "\\1", startOFF$values)
      startOFF$playerID <- sub("start,([a-z0-9\\-]+),.*", "\\1", startOFF$values)
      startOFF <- startOFF[order(startOFF$ID,startOFF$team),]
      startOFF <- dcast(startOFF, ID ~ team + BatOrd, value.var="playerID")
      names(startOFF) <- sub("^0", "away", sub("^1", "home", names(startOFF)))
      
      # combine with INFO
      INFO <- merge(INFO, merge(startOFF, startDEF, by="ID"), by="ID")
      
      # PLAYS AND SUBS but keep chronological order
      TEMP <- rbindlist(sapply(with(DF[grepl("^(play|sub)", DF$EVN),], tapply(EVN, ID, FUN=t)), function(x) list(data.frame(x, stringsAsFactors = FALSE))), fill=TRUE)
      ALLG <- stack(TEMP)
      ALLG$gameID <- rep(INFO$ID, length(TEMP))
      ALLG <- ALLG[order(ALLG$gameID, ALLG$ind),]
      ALLG$ID <- (2016*1000000+1):(2016*1000000+nrow(ALLG)) # playID - by year
      ALLG <- ALLG[,c(4,3,1)]
      ALLG <- ALLG[!is.na(ALLG$values),]
      ALLG$type <- sub(",.*", "", ALLG$values)
      
      # handle plays
      ply_row <- grep("play", ALLG$values)
      ALLG$inning[ply_row] <- sub("^play,([0-9]+),.*", "\\1", ALLG$values[ply_row])
      ALLG$team[ply_row] <- sub("^play,([0-9]+),([0,1]),.*", "\\2", ALLG$values[ply_row])
      ALLG$playerID[ply_row] <- sub("^play,([0-9]+),([0,1]),([a-z0-9\\-]+),.*", "\\3", ALLG$values[ply_row])
      ALLG$event[ply_row] <- sub(".*,", "", ALLG$values[ply_row])
      
      # handle substitutions
      sub_row <- grep("sub", ALLG$values)
      ALLG$inning[sub_row] <- ALLG$inning[sub_row + 1]
      ALLG$team[sub_row] <- ALLG$team[sub_row + 1] # just use the same team as "top/bottom" of inning 
      #ALLG$team[sub_row] <- sub("sub,.*,.*,([0,1]),([0-9]+),([0-9]+)$", "\\1", ALLG$team[sub_row])
      ALLG$playerID[sub_row] <- sub("^sub,([a-z0-9\\-]+),.*", "\\1", ALLG$playerID[sub_row])
      ALLG$event[sub_row] <- "SUBSTITUTION"
      
      
      
      ### CLEANING UP THE CODE A BIT - from version 1.1.6 and onward, using the following code ###
      CLN <- data.frame(ID=ALLG$ID, GP=ALLG$gameID, Inning=ALLG$inning, Team=ALLG$team, playerID=ALLG$playerID, Event=ALLG$event, stringsAsFactors = FALSE)
      CLN$Event <- gsub("\\!", "", CLN$Event)
      # max(str_count(CLN$Event, "\\.")) # just checking for more than 1 period
      # [1] 1
      
      # get the runner advances/outs
      CLN$Runners[grepl("\\.", CLN$Event)] <- sub(".*\\.", "", CLN$Event[grepl("\\.", CLN$Event)])
      
      # get the play, / or . whichever comes first
      CLN$Play[grepl("(/|\\.)", CLN$Event)] <- 
            sub("(/|\\.).*", "", CLN$Event[grepl("(/|\\.)", CLN$Event)])
      CLN$Play[is.na(CLN$Play)] <- CLN$Event[is.na(CLN$Play)]
      
      ###############################################################################
      # sort these plays, handle the batter runner. then deal with base runners     #
      # watch for the steals and errors!                                            #
      ###############################################################################
      
      ## set up NA bases for AB (at-bat) and PE (post-event)
      CLN$Outs <- 0
      CLN$PE_3B <- CLN$PE_2B <- CLN$PE_1B <- CLN$AB_Outs <- CLN$AB_3B <- CLN$AB_2B <- CLN$AB_1B <- NA
      CLN$AB_Outs <- CLN$PE_Outs <- CLN$Runs <- 0
      
      ## adding a backup here for manual runs ##
      # BKUP <- CLN
      
      # handle all regular hits, walks, strikeouts #
      tg_Ks <- grepl("^K", CLN$Play) & !grepl("(B-)|(BX[1-3H]\\([1-9]*E[1-9]*)", CLN$Runners)
      tg_Wk <- grepl("^(W|IW)", CLN$Play) & !grepl("^WP", CLN$Play) & !grepl("B-[2-H]", CLN$Runners) # allow redundant B-1
      tg_Sng <- grepl("^S[1-9]", CLN$Play) & !grepl("((B-[23H])|(BX[123H]))", CLN$Runners) # allow redundant B-1
      tg_Dbl <- grepl("^D([1-9]|GR)", CLN$Play) & !grepl("B-3|BX3|BX2", CLN$Runners) # allow redundant B-2
      tg_Trp <- grepl("^T[1-9]", CLN$Play) & !grepl("B-H|BXH|BX3", CLN$Runners) # allow redundant B-3
      tg_HR <- grepl("^HR", CLN$Play) & !grepl("B(-|X)", CLN$Runners)
      
      # handle all regular hits with errors causing batter advance #
      tg_H2 <- grepl("^S[1-9]", CLN$Play) & grepl("B-2(\\(([1-9]*E[1-9]+|TH))?", CLN$Runners)
      tg_S3 <- grepl("^S[1-9]", CLN$Play) & grepl("B-3(\\(([1-9]*E[1-9]+|TH))?", CLN$Runners)
      tg_SH <- grepl("^S[1-9]", CLN$Play) & grepl("B-H(\\(([1-9]*E[1-9]+|TH))?", CLN$Runners)
      tg_H3 <- grepl("^D[1-9]", CLN$Play) & grepl("B-3(\\(([1-9]*E[1-9]+|TH))?", CLN$Runners)
      tg_DH <- grepl("^D[1-9]", CLN$Play) & grepl("B-H(\\(([1-9]*E[1-9]+|TH))?", CLN$Runners)
      tg_HH <- grepl("^T[1-9]", CLN$Play) & grepl("B-H([\\(NUR\\)])*\\([1-9]*E[1-9]+", CLN$Runners)
      
      # handle all regular hits with errors when batter should have been out at final base #
      tg_E2 <- grepl("^S[1-9]", CLN$Play) & grepl("BX2(\\(([1-9]*E[1-9]+|TH))", CLN$Runners)
      tg_ES <- grepl("^S[1-9]", CLN$Play) & grepl("BX3(\\(([1-9]*E[1-9]+|TH))", CLN$Runners)
      tg_SE <- grepl("^S[1-9]", CLN$Play) & grepl("BXH(\\(([1-9]*E[1-9]+|TH))", CLN$Runners)
      tg_E3 <- grepl("^D[1-9]", CLN$Play) & grepl("BX3(\\(([1-9]*E[1-9]+|TH))", CLN$Runners)
      tg_ED <- grepl("^D[1-9]", CLN$Play) & grepl("BXH(\\(([1-9]*E[1-9]+|TH))", CLN$Runners)
      tg_ET <- grepl("^T[1-9]", CLN$Play) & grepl("BXH([\\(NUR\\)])*\\([1-9]*E[1-9]+", CLN$Runners)
      
      # all HR that recorded redundant B-H (to indicated un-earned, etc.)
      tg_HU <- grepl("^HR.*B-H", CLN$Event)
      
      # all strikeouts went bad lol
      tg_K1 <- grepl("^K.*(B-1|BX1\\([1-9]*E[1-9]*)", CLN$Event)
      tg_K2 <- grepl("^K.*(B-2|BX2\\([1-9]*E[1-9]*)", CLN$Event)
      tg_K3 <- grepl("^K.*(B-3|BX3\\([1-9]*E[1-9]*)", CLN$Event)
      tg_KH <- grepl("^K.*(B-H|BXH\\([1-9]*E[1-9]*)", CLN$Event)
      
      # all walks went bad
      tg_W2 <- grepl("^(W|IW)", CLN$Play) & grepl("B-2", CLN$Runners)
      tg_W3 <- grepl("^(W|IW)", CLN$Play) & grepl("B-3", CLN$Runners)
      tg_W4 <- grepl("^(W|IW)", CLN$Play) & grepl("B-H", CLN$Runners)
      
      # handle force outs that batter made it to base, include ERRORS for all
      tg_FO <- grepl("FO", CLN$Event) & !grepl("B(-|X)[2-3H]", CLN$Runners)
      tg_2F <- grepl("FO", CLN$Event) & grepl("(B-2)|(BX2\\([1-9]*E[1-9]*)", CLN$Runners)
      tg_3F <- grepl("FO", CLN$Event) & grepl("(B-3)|(BX3\\([1-9]*E[1-9]*)", CLN$Runners)
      tg_HF <- grepl("FO", CLN$Event) & grepl("(B-H)|(BXH\\([1-9]*E[1-9]*)", CLN$Runners)
      
      # handle fielder's choice that batter made it to base, include ERRORS for all
      tg_FC <- grepl("FC", CLN$Event) & !grepl("B(-|X)[2-3H]", CLN$Runners)
      tg_F2 <- grepl("FC", CLN$Event) & grepl("(B-2)|(BX2\\([1-9]*E[1-9]*)", CLN$Runners)
      tg_F3 <- grepl("FC", CLN$Event) & grepl("(B-3)|(BX3\\([1-9]*E[1-9]*)", CLN$Runners)
      tg_FH <- grepl("FC", CLN$Event) & grepl("(B-H)|(BXH\\([1-9]*E[1-9]*)", CLN$Runners)
      
      # handle all GDP where batter runner is safe
      tg_P1 <- grepl("GDP.*(B-1|BX1\\([1-9]?E[1-9]\\))", CLN$Event)
      tg_P2 <- grepl("GDP.*(BX2\\([1-9]?E[1-9]\\))", CLN$Event)
      tg_P3 <- grepl("GDP.*(BX3\\([1-9]?E[1-9]\\))", CLN$Event)
      tg_PH <- grepl("GDP.*(BXH\\([1-9]?E[1-9]\\))", CLN$Event)
      
      # handle all ERRORS not FO or FC
      tg_1E <- grepl("^(E|[1-9]E)[1-9]", CLN$Event) & !grepl("FC|FO", CLN$Event) & !grepl("B(-|X)[2-3H]", CLN$Runners)
      tg_2E <- grepl("^(E|[1-9]E)[1-9]", CLN$Event) & !grepl("FC|FO", CLN$Event) & grepl("(B-2)|(BX2\\([1-9]*E[1-9]*)", CLN$Runners)
      tg_3E <- grepl("^(E|[1-9]E)[1-9]", CLN$Event) & !grepl("FC|FO", CLN$Event) & grepl("(B-3)|(BX3\\([1-9]*E[1-9]*)", CLN$Runners)
      tg_HE <- grepl("^(E|[1-9]E)[1-9]", CLN$Event) & !grepl("FC|FO", CLN$Event) & grepl("(B-H)|(BXH\\([1-9]*E[1-9]*)", CLN$Runners)
      
      # catcher interference - no other advances possible, always immediately dead ball.
      tg_CI <- grepl("^C", CLN$Event) & !grepl("^CS", CLN$Event)
      
      # hit by pitch - also dead ball immediately.
      tg_HP <- grepl("^HP", CLN$Event)
      
      # a runner is hit by batted ball ... wow lol #
      tg_BR <- grepl("^S.*BR", CLN$Event) 
      # single is still awarded, the out still recorded: [1-3]X[1-3H]
      
      # move the batter runner
      CLN$PE_1B[tg_Wk | tg_Sng | tg_K1 | tg_FO | tg_FC | tg_P1 | tg_1E | tg_CI | tg_HP | tg_BR] <- 
            CLN$playerID[tg_Wk | tg_Sng | tg_K1 | tg_FO | tg_FC | tg_P1 | tg_1E | tg_CI | tg_HP | tg_BR]
      CLN$PE_2B[tg_Dbl | tg_H2 | tg_E2 | tg_K2 | tg_W2 | tg_2F | tg_F2 | tg_P2 | tg_2E] <- 
            CLN$playerID[tg_Dbl | tg_H2 | tg_E2 | tg_K2 | tg_W2 | tg_2F | tg_F2 | tg_P2 | tg_2E]
      CLN$PE_3B[tg_Trp | tg_S3 | tg_H3 | tg_ES | tg_E3 | tg_K3 | tg_W3 | tg_3F | tg_F3 | tg_P3 | tg_3E] <- 
            CLN$playerID[tg_Trp | tg_S3 | tg_H3 | tg_ES | tg_E3 | tg_K3 | tg_W3 | tg_3F | tg_F3 | tg_P3 | tg_3E]
      
      # score the batter runner
      CLN$Runs[tg_HR | tg_SH | tg_DH | tg_HH | tg_SE | tg_ED | tg_ET | 
                     tg_KH | tg_W4 | tg_HF | tg_FH | tg_PH | tg_HE | tg_HU] <- 1
       
	# # check if other ways for batter to get on base that was missed
	# print(unique(CLN$Event[!(tg_Wk | tg_Sng | tg_K1 | tg_FO | tg_FC | tg_P1 | tg_1E | tg_CI |  
	#                                tg_HP | tg_BR | tg_Dbl | tg_H2 | tg_E2 | tg_K2 | tg_W2 | tg_2F | 
	#                                tg_F2 | tg_P2 | tg_2E | tg_Trp | tg_S3 | tg_H3 | tg_ES | tg_E3 | 
	#                                tg_K3 | tg_W3 | tg_3F | tg_F3 | tg_P3 | tg_3E) & 
	#                              grepl("B-[1-3]", CLN$Runners)]))
	# # output should be 0, nothing
	# 
	# print(unique(CLN$Event[!(tg_Wk | tg_Sng | tg_K1 | tg_FO | tg_FC | tg_P1 | tg_1E | tg_CI |  
	#                                tg_HP | tg_BR | tg_Dbl | tg_H2 | tg_E2 | tg_K2 | tg_W2 | tg_2F | 
	#                                tg_F2 | tg_P2 | tg_2E | tg_Trp | tg_S3 | tg_H3 | tg_ES | tg_E3 | 
	#                                tg_K3 | tg_W3 | tg_3F | tg_F3 | tg_P3 | tg_3E) & 
	#                              grepl("BX[1-3]", CLN$Runners) & 
	#                              !grepl("BX[1-3]\\([1-9TH/]+\\)", CLN$Runners)]))
      # output should only be 0, ignoring all the outs
      
      
	##########################################
      # now deal with batters safe on errors   #
      ##########################################
	
      # batter on base from error #
	E_B <- grepl("^[1-9]*E[1-9]+", CLN$Event) & !grepl("B(-|X)", CLN$Event)
	E_1 <- grepl("^[1-9]*E[1-9]+", CLN$Event) & grepl("B-1|BX1\\([1-9]*E[1-9]+", CLN$Event)
	E_2 <- grepl("^[1-9]*E[1-9]+", CLN$Event) & grepl("B-2|BX2\\([1-9]*E[1-9]+", CLN$Event)
	E_3 <- grepl("^[1-9]*E[1-9]+", CLN$Event) & grepl("B-3|BX3\\([1-9]*E[1-9]+", CLN$Event)
	E_H <- grepl("^[1-9]*E[1-9]+", CLN$Event) & grepl("B-H|BXH\\([1-9]*E[1-9]+", CLN$Event)
	CLN$PE_1B[E_B | E_1] <- CLN$playerID[E_B | E_1]
	CLN$PE_2B[E_2] <- CLN$playerID[E_2]
	CLN$PE_3B[E_3] <- CLN$playerID[E_3]
	CLN$Runs[E_H] <- CLN$Runs[E_H] + 1
	
      # runner is hit by batted ball ... wow lol #
      BR_scn <- grepl("^S.*BR", CLN$Event) # single is still awarded, the out still recorded: [1-3]X[1-3H]
      CLN$PE_1B[BR_scn] <- CLN$playerID[BR_scn]
      
	# Catcher interference, redundant B-1 allowed. unless BX-ed
      C_INT <- grepl("^C/E[1-9].*(B-1)?", CLN$Event)
      CLN$PE_1B[C_INT] <- CLN$playerID[C_INT]
      
	# WALK turned into double #
      WK_2B <- grepl("W.*B-2", CLN$Event)
      CLN$PE_2B[WK_2B] <- CLN$playerID[WK_2B]
      CLN$PE_1B[WK_2B] <- NA # remove batter from 1st which is automatic from Walks above
      
	# strikeout, batter makes it to first on error
      K_BX1E <- grepl("^K.BX1\\([1-9]*E[1-9]*", CLN$Event)
      CLN$PE_1B[K_BX1E] <- CLN$playerID[K_BX1E]
      CLN$Outs[K_BX1E & CLN$Outs > 0] <- CLN$Outs[K_BX1E & CLN$Outs > 0] - 1      
      
      # PB / WP / HP / Error # NEGATE THE OUT ON K'S
      No_K <- grepl("K(\\+)?(WP|PB|E[1-9])?.*B-1", CLN$Event) # only negate these outs; send batter to base
      CLN$Outs[No_K] <- 0
      CLN$PE_1B[No_K] <- CLN$playerID[No_K]
      
      # K/FO - this is a weird one, but probably a bounce to plate strike out and just force out @ home
      K_FO <- grepl("K/FO\\.3XH", CLN$Event)
      CLN$Outs[K_FO] <- 1
      
      
	##########################
      # now deal with all outs #
      ##########################
	
	# batter outs
	OB_K <- grepl("^K", CLN$Play) & !grepl("(B-|BX[1-H][1-9]*E[1-9])", CLN$Play)
	FO_B <- grepl("^[1-9]+", CLN$Play) & !grepl("FO|DP|TP|E[1-9]", CLN$Event)
	FC_B <- grepl("^FC", CLN$Play) & !grepl("B(-|X)", CLN$Event)
	CLN$Outs[OB_K | FO_B | FC_B] <- CLN$Outs[OB_K | FO_B | FC_B] + 1
	
	# runner outs
	ORUN <- grepl("[1-3]X[1-3H]", CLN$Runners) & !grepl("[1-3]X[1-3H]([\\(NUR\\)])*\\([1-9]*E[1-9]+", CLN$Runners)
      CLN$Outs[ORUN] <- CLN$Outs[ORUN] + 1
      
      # force outs / fielder's choice #
      FO_R <- grepl("\\([1-3].*/FO", CLN$Event)
      FC_R <- grepl("^FC", CLN$Play) & grepl("B-[1-3H]", CLN$Event)
      FC_X <- grepl("^FC", CLN$Play) & grepl("BX", CLN$Event)
      CLN$Outs[FO_R | FC_R] <- CLN$Outs[FO_R | FC_R] + 1
      CLN$Outs[FC_X] <- CLN$Outs[FC_X] + str_count(CLN$Play[FC_X], "X")
      
      # DOUBLE / TRIPLE PLAYS #
      DP_F1 <- grepl("^[1-9]+.*\\(1.*DP", CLN$Event) & !grepl("[B1-3]X[1-3H]", CLN$Event)
      DP_F2 <- grepl("^[1-9]+.*\\(2.*DP", CLN$Event) & !grepl("[B1-3]X[1-3H]", CLN$Event)
      DP_F3 <- grepl("^[1-9]+.*\\(3.*DP", CLN$Event) & !grepl("[B1-3]X[1-3H]", CLN$Event)
      CLN$Outs[grepl("DP", CLN$Event)] <- 2
      CLN$Outs[grepl("TP", CLN$Event)] <- 3
	
	# Caught Stealing or Picked Off with on errors
	CSPO <- grepl("^(CS|PO)", CLN$Play) & !grepl("[1-9]*E[1-9]", CLN$Play)
	CLN$Outs[CSPO] <- CLN$Outs[CSPO] + 1
	
	# return CLN #
      return(CLN)
      
}

################################
################################


################################
##     Recursive Function     ##
################################

# 1. Transfer runners to next at-bat
# 2. Assign all runners moving - include errors
# 3. Account for end of inning
# 4. Assign all runners not moved - include errors
# 5. Handle Stolen Bases - include errors
# 6. Assign all runners out - include errors
# 7. Check for recursive function ending

# recursive function that will continue advancing (some removing) runners until inning complete.
adv_runnersNA <- function (CLN) {
      
      ## generate temp table to compare to after advancing runners ##
      TMP <- CLN
      
      ## advance the runners per usual ##
	all_plyExcp1st <- 2:nrow(CLN)
	R1X1 <- grepl("1X1\\([1-9]*E[1-9]+", CLN$Runners) # error but no advance
      R1_2 <- grepl("1-2", CLN$Runners) | grepl("1X2\\([1-9]*E[1-9]+", CLN$Runners)
      R1_3 <- grepl("1-3", CLN$Runners) | grepl("1X3\\([1-9]*E[1-9]+", CLN$Runners)
      R2X2 <- grepl("2X2\\([1-9]*E[1-9]+", CLN$Runners) # error but no advance
      R2_3 <- grepl("2-3", CLN$Runners) | grepl("2X3\\([1-9]*E[1-9]+", CLN$Runners)
      R3X3 <- grepl("3X3\\([1-9]*E[1-9]+", CLN$Runners) # error but no advance
      # assign bases #
	CLN$AB_1B[all_plyExcp1st] <- CLN$PE_1B[all_plyExcp1st-1]
      CLN$PE_1B[R1X1] <- CLN$AB_1B[R1X1]
      CLN$PE_2B[R1_2] <- CLN$AB_1B[R1_2]
      CLN$AB_2B[all_plyExcp1st] <- CLN$PE_2B[all_plyExcp1st-1]
      CLN$PE_2B[R2X2] <- CLN$AB_2B[R2X2]
      CLN$PE_3B[R1_3] <- CLN$AB_1B[R1_3]
      CLN$PE_3B[R2_3] <- CLN$AB_2B[R2_3]
      CLN$AB_3B[all_plyExcp1st] <- CLN$PE_3B[all_plyExcp1st-1]
      CLN$PE_3B[R3X3] <- CLN$AB_3B[R3X3]
      
      ## ignore the change of inning inheriting of runners ##
      chg_inning <- data.table:::uniqlist(CLN[!is.na(CLN$Team),3:4])
	# assign bases #
      CLN$PE_1B[chg_inning-1] <- NA
      CLN$PE_2B[chg_inning-1] <- NA
      CLN$PE_3B[chg_inning-1] <- NA
      CLN$AB_1B[chg_inning] <- NA
      CLN$AB_2B[chg_inning] <- NA
      CLN$AB_3B[chg_inning] <- NA
      
      ## inherit runners when they did not move -- when no runners advanced ##
      CLN$PE_1B[is.na(CLN$Runners) & !is.na(CLN$AB_1B) & !grepl("SB|PO|CS|BK|DP|TP", CLN$Play)] <-
            CLN$AB_1B[is.na(CLN$Runners) & !is.na(CLN$AB_1B) & !grepl("SB|PO|CS|BK|DP|TP", CLN$Play)]
      CLN$PE_2B[is.na(CLN$Runners) & !is.na(CLN$AB_2B) & !grepl("SB|PO|CS|BK|DP|TP", CLN$Play)] <-
            CLN$AB_2B[is.na(CLN$Runners) & !is.na(CLN$AB_2B) & !grepl("SB|PO|CS|BK|DP|TP", CLN$Play)]
      CLN$PE_3B[is.na(CLN$Runners) & !is.na(CLN$AB_3B) & !grepl("SB|PO|CS|BK|DP|TP", CLN$Play)] <-
            CLN$AB_3B[is.na(CLN$Runners) & !is.na(CLN$AB_3B) & !grepl("SB|PO|CS|BK|DP|TP", CLN$Play)]
      
      ## inherit runners when explicity mentioned that they did not move ##
	R1_1 <- grepl("1-1", CLN$Runners)
      R2_2 <- grepl("2-2", CLN$Runners)
      R3_3 <- grepl("3-3", CLN$Runners)
	# assign bases #
      CLN$PE_1B[R1_1] <- CLN$AB_1B[R1_1]
      CLN$PE_2B[R2_2] <- CLN$AB_2B[R2_2]
      CLN$PE_3B[R3_3] <- CLN$AB_3B[R3_3]
	
	## inherit runners on NP or SUBSTITUTION ##
	NP_ST <- grepl("^(NP|SUBSTITUTION)", CLN$Event)
      # assign bases #
      CLN$PE_1B[NP_ST] <- CLN$AB_1B[NP_ST]
      CLN$PE_2B[NP_ST] <- CLN$AB_2B[NP_ST]
      CLN$PE_3B[NP_ST] <- CLN$AB_3B[NP_ST]
	
	# WILD PITCH?#
	
      ## inherit runners that did not score or get put out but there were runner advances ##
      # need to exclude double / triple plays and force outs!
      CLN$PE_1B[!is.na(CLN$Runners) & !compareNA(CLN$PE_1B, CLN$playerID) & !grepl("TP|DP|FO", CLN$Event) & 
                      !grepl("1(-|X)[123H]", CLN$Runners) & !is.na(CLN$AB_1B)] <-
            CLN$AB_1B[!is.na(CLN$Runners) & !compareNA(CLN$PE_1B, CLN$playerID) & !grepl("TP|DP|FO", CLN$Event) & 
                            !grepl("1(-|X)[123H]", CLN$Runners) & !is.na(CLN$AB_1B)]
      CLN$PE_2B[!is.na(CLN$Runners) & !compareNA(CLN$PE_2B, CLN$playerID) & !grepl("TP|DP|FO", CLN$Event) & 
                      !grepl("2(-|X)[23H]", CLN$Runners) & !is.na(CLN$AB_2B)] <-
            CLN$AB_2B[!is.na(CLN$Runners) & !compareNA(CLN$PE_2B, CLN$playerID) & !grepl("TP|DP|FO", CLN$Event) & 
                            !grepl("2(-|X)[23H]", CLN$Runners) & !is.na(CLN$AB_2B)]
      CLN$PE_3B[!is.na(CLN$Runners) & !compareNA(CLN$PE_3B, CLN$playerID) & !grepl("TP|DP|FO", CLN$Event) & 
                      !grepl("3(-|X)[3H]", CLN$Runners) & !is.na(CLN$AB_3B)] <-
            CLN$AB_3B[!is.na(CLN$Runners) & !compareNA(CLN$PE_3B, CLN$playerID) & !grepl("TP|DP|FO", CLN$Event) & 
                            !grepl("3(-|X)[3H]", CLN$Runners) & !is.na(CLN$AB_3B)]
      # not moving in defensive indifference done above ^ #
      
      # handle the force outs no advances #
      CLN$PE_1B[!is.na(CLN$Runners) & !compareNA(CLN$PE_1B, CLN$playerID) & !grepl("1(-|X)", CLN$Runners) & 
                      grepl(".*FO", CLN$Event) & !grepl("^[1-9]+\\(1\\)", CLN$Event) & !is.na(CLN$AB_1B)] <- 
            CLN$AB_1B[!is.na(CLN$Runners) & !compareNA(CLN$PE_1B, CLN$playerID) & grepl("1(-|X)", CLN$Runners) & 
                            grepl(".*FO", CLN$Event) & !grepl("^[1-9]+\\(1\\)", CLN$Event) & !is.na(CLN$AB_1B)]
      CLN$PE_2B[!is.na(CLN$Runners) & !compareNA(CLN$PE_2B, CLN$playerID) & !grepl("2(-|X)", CLN$Runners) & 
                      grepl(".*FO", CLN$Event) & !grepl("^[1-9]+\\(2\\)", CLN$Event) & !is.na(CLN$AB_2B)] <- 
            CLN$AB_2B[!is.na(CLN$Runners) & !compareNA(CLN$PE_2B, CLN$playerID) & !grepl("2(-|X)", CLN$Runners) & 
                            grepl(".*FO", CLN$Event) & !grepl("^[1-9]+\\(2\\)", CLN$Event) & !is.na(CLN$AB_2B)]
      CLN$PE_3B[!is.na(CLN$Runners) & !compareNA(CLN$PE_3B, CLN$playerID) & !grepl("3(-|X)", CLN$Runners) & 
                      grepl(".*FO", CLN$Event) & !grepl("^[1-9]+\\(3\\)", CLN$Event) & !is.na(CLN$AB_3B)] <- 
            CLN$AB_3B[!is.na(CLN$Runners) & !compareNA(CLN$PE_3B, CLN$playerID) & !grepl("3(-|X)", CLN$Runners) & 
                            grepl(".*FO", CLN$Event) & !grepl("^[1-9]+\\(3\\)", CLN$Event) & !is.na(CLN$AB_3B)]
      
      ## handle stolen bases ##
      # okay to loop, the runner may not have stolen right arriving to that base #
      CLN$PE_2B[!compareNA(CLN$AB_1B,CLN$PE_2B) & grepl("SB2", CLN$Event) & !grepl("1(-|X)", CLN$Event)] <- 
            CLN$AB_1B[!compareNA(CLN$AB_1B,CLN$PE_2B) & grepl("SB2", CLN$Event) & !grepl("1(-|X)", CLN$Event)]
      CLN$PE_3B[!compareNA(CLN$AB_2B,CLN$PE_3B) & grepl("SB3", CLN$Event) & !grepl("2(-|X)", CLN$Event)] <- 
            CLN$AB_2B[!compareNA(CLN$AB_2B,CLN$PE_3B) & grepl("SB3", CLN$Event) & !grepl("2(-|X)", CLN$Event)]
      
      # case where 1st base runner did not steal on a stolen base at 3B or H #
      CLN$PE_1B[(grepl("SB(3|H)", CLN$Event) | grepl("(PO2|PO3|CS3)", CLN$Event)) & !is.na(CLN$AB_1B) & 
                      !grepl("SB2", CLN$Event) & !grepl("1(-|X)", CLN$Event)] <- 
            CLN$AB_1B[(grepl("SB(3|H)", CLN$Event) | grepl("(PO2|PO3|CS3)", CLN$Event)) 
                      & !is.na(CLN$AB_1B) & !grepl("SB2", CLN$Event) & !grepl("1(-|X)", CLN$Event)]
      
      # case where 3rd base runner did not steal on a stolen base at 2B #
      CLN$PE_3B[(grepl("SB2", CLN$Event) | grepl("(PO1|PO2|CS2)", CLN$Event)) & !is.na(CLN$AB_3B) & 
                      !grepl("SB(3|H)", CLN$Event) & !grepl("3(-|X)", CLN$Event)] <- 
            CLN$AB_3B[(grepl("SB2", CLN$Event) | grepl("(PO1|PO2|CS2)", CLN$Event)) & 
                            !is.na(CLN$AB_3B) & !grepl("SB(3|H)", CLN$Event) & !grepl("3(-|X)", CLN$Event)]
      
      # double check bases when stealing lol #
      CLN$PE_1B[CLN$PE_1B==CLN$PE_2B & grepl("SB2", CLN$Event) & !grepl("1(-|X)(3|H)", CLN$Event)] <- NA
      CLN$PE_2B[CLN$PE_2B==CLN$PE_3B & grepl("SB3", CLN$Event) & !grepl("2(-|X)H", CLN$Event)] <- NA
      CLN$PE_3B[CLN$PE_3B==CLN$AB_3B & grepl("SBH", CLN$Event)] <- NA
      
      ## handle pick offs and caught stealing ##
      # inherit runners when they did not move #
      CLN$PE_1B[is.na(CLN$Runners) & !is.na(CLN$AB_1B) & grepl("PO|CS", CLN$Play) & 
                      !grepl("PO1|CS2", CLN$Play) & !grepl("E[1-9]", CLN$Play)] <- 
            CLN$AB_1B[is.na(CLN$Runners) & !is.na(CLN$AB_1B) & grepl("PO|CS", CLN$Play) & 
                            !grepl("PO1|CS2", CLN$Play) & !grepl("E[1-9]", CLN$Play)]
      CLN$PE_2B[is.na(CLN$Runners) & !is.na(CLN$AB_2B) & grepl("PO|CS", CLN$Play) & 
                      !grepl("PO2|CS3", CLN$Play) & !grepl("E[1-9]", CLN$Play)] <- 
            CLN$AB_2B[is.na(CLN$Runners) & !is.na(CLN$AB_2B) & grepl("PO|CS", CLN$Play) & 
                            !grepl("PO2|CS3", CLN$Play) & !grepl("E[1-9]", CLN$Play)]
      CLN$PE_3B[is.na(CLN$Runners) & !is.na(CLN$AB_3B) & grepl("PO|CS", CLN$Play) & 
                      !grepl("PO3|CSH", CLN$Play) & !grepl("E[1-9]", CLN$Play)] <- 
            CLN$AB_3B[is.na(CLN$Runners) & !is.na(CLN$AB_3B) & grepl("PO|CS", CLN$Play) & 
                            !grepl("PO3|CSH", CLN$Play) & !grepl("E[1-9]", CLN$Play)]
      # inherit runner when NOT picked off but did not advance #
      CLN$PE_1B[is.na(CLN$Runners) & !is.na(CLN$AB_1B) & grepl("PO1\\([1-9]*E", CLN$Play)] <- 
            CLN$AB_1B[is.na(CLN$Runners) & !is.na(CLN$AB_1B) & grepl("PO1\\([1-9]*E", CLN$Play)]
      CLN$PE_2B[is.na(CLN$Runners) & !is.na(CLN$AB_2B) & grepl("PO2\\([1-9]*E", CLN$Play)] <- 
            CLN$AB_2B[is.na(CLN$Runners) & !is.na(CLN$AB_2B) & grepl("PO2\\([1-9]*E", CLN$Play)]
      CLN$PE_3B[is.na(CLN$Runners) & !is.na(CLN$AB_3B) & grepl("PO3\\([1-9]*E", CLN$Play)] <- 
            CLN$AB_3B[is.na(CLN$Runners) & !is.na(CLN$AB_3B) & grepl("PO3\\([1-9]*E", CLN$Play)]
      
      ## fielders' choice / force outs ##
      # batter makes it to first on force out, including on errors where B moves to 1-3/H #
	FO_B <- grepl("^[1-9]+", CLN$Play) & !grepl("FO|DP|TP|E[1-9]", CLN$Event)
      FO_1 <- grepl("\\(1.*/FO", CLN$Event)
      FO_2 <- grepl("\\(2.*/FO", CLN$Event)
      FO_3 <- grepl("\\(3.*/FO", CLN$Event)
      FC_B <- grepl("^FC", CLN$Play) & !grepl("B(-|X)", CLN$Event)
      FC_1 <- grepl("^FC", CLN$Play) & grepl("B-1", CLN$Event)
      FC_2 <- grepl("^FC", CLN$Play) & grepl("B-2", CLN$Event)
      FC_3 <- grepl("^FC", CLN$Play) & grepl("B-3", CLN$Event)
      FC_H <- grepl("^FC", CLN$Play) & grepl("B-H", CLN$Event)
      FC_X <- grepl("^FC", CLN$Play) & grepl("BX", CLN$Event)
	# assign bases #
      CLN$PE_1B[(FO_1 | FO_2 | FO_3 | FC_B) & !grepl("B(-|X)", CLN$Event)] <- 
            CLN$playerID[(FO_1 | FO_2 | FO_3 | FC_B) & !grepl("B(-|X)", CLN$Event)]
      CLN$PE_1B[(FO_1 | FO_2 | FO_3 | FC_1) & grepl("B(-|X)1", CLN$Event)] <- 
            CLN$playerID[(FO_1 | FO_2 | FO_3 | FC_1) & grepl("B(-|X)1", CLN$Event)]
      CLN$PE_2B[(FO_1 | FO_2 | FO_3 | FC_2) & grepl("B(-|X)2", CLN$Event)] <- 
            CLN$playerID[(FO_1 | FO_2 | FO_3 | FC_2) & grepl("B(-|X)2", CLN$Event)]
      CLN$PE_3B[(FO_1 | FO_2 | FO_3 | FC_3) & grepl("B(-|X)3", CLN$Event)] <- 
            CLN$playerID[(FO_1 | FO_2 | FO_3 | FC_3) & grepl("B(-|X)3", CLN$Event)]
      CLN$Runs[(FO_1 | FO_2 | FO_3 | FC_H) & grepl("B(-|X)H", CLN$Event)] <- 
            CLN$Runs[(FO_1 | FO_2 | FO_3 | FC_H) & grepl("B(-|X)H", CLN$Event)]
      
      ## routine double plays ##
	DP_F1 <- grepl("^[1-9]+.*\\(1.*DP", CLN$Event) & !grepl("[B1-3]X[1-3H]", CLN$Event)
      DP_F2 <- grepl("^[1-9]+.*\\(2.*DP", CLN$Event) & !grepl("[B1-3]X[1-3H]", CLN$Event)
      DP_F3 <- grepl("^[1-9]+.*\\(3.*DP", CLN$Event) & !grepl("[B1-3]X[1-3H]", CLN$Event)
	# assign bases #
      CLN$PE_1B[DP_F1] <- NA
      CLN$PE_2B[DP_F2] <- NA
      CLN$PE_3B[DP_F3] <- NA
      # 2nd & 3rd or 3rd and home or 2nd and home #
      CLN$PE_1B[(DP_F1 & DP_F2) | (DP_F2 & DP_F3) | (DP_F1 & DP_F3)] <- 
            CLN$playerID[(DP_F1 & DP_F2) | (DP_F2 & DP_F3) | (DP_F1 & DP_F3)]
      # 1B runner is safe at 2B if outs at 3rd and home #
      CLN$PE_2B[(DP_F2 & DP_F3)] <- CLN$AB_2B[(DP_F2 & DP_F3)]
      # 2B runner is safe at 3B if outs are 2nd and home #
      CLN$PE_3B[(DP_F1 & DP_F3)] <- CLN$AB_3B[(DP_F1 & DP_F3)]
      
      ## non-routine double plays ## ## might need more case(s) ##
	DP_1X <- grepl("^[1-9]+.*DP.*X", CLN$Event) & !grepl("X.*X", CLN$Event)
      DP_2X <- grepl("^[1-9]+.*DP.*X", CLN$Event) & grepl("X.*X", CLN$Event)
      # batter is out, another runner is out #
      if (any(DP_1X)) {
            # 1B runner is out
            CLN$PE_1B[DP_1X & grepl("(^[1-9]+\\(1\\))|(1X)", CLN$Event)] <- NA
            # 1B runner safe and did not advance
            CLN$PE_1B[DP_1X & !grepl("(^[1-9]+\\(1\\))|(1(-|X))", CLN$Event)] <- 
                  CLN$AB_1B[DP_1X & !grepl("(^[1-9]+\\(1\\))|(1(-|X))", CLN$Event)]
            
            # 2B runner is out
            CLN$PE_2B[DP_1X & grepl("(^[1-9]+\\(2\\))|(2X)", CLN$Event) & !grepl("1-2", CLN$Event)] <- NA
            # 2B runner safe and did not advance
            CLN$PE_2B[DP_1X & !grepl("(^[1-9]+\\(2\\))|(2(-|X))", CLN$Event) & !grepl("1-2", CLN$Event)] <- 
                  CLN$AB_2B[DP_1X & !grepl("(^[1-9]+\\(2\\))|(2(-|X))", CLN$Event) & !grepl("1-2", CLN$Event)]
            
            # 3B runner is out
            CLN$PE_3B[DP_1X & grepl("(^[1-9]+\\(3\\))|(3X)", CLN$Event) & !grepl("(1|2)-3", CLN$Event)] <- NA
            # 3B runner safe and did not advance
            CLN$PE_3B[DP_1X & !grepl("(^[1-9]+\\(3\\))|(3(-|X))", CLN$Event) & !grepl("(1|2)-3", CLN$Event)] <- 
                  CLN$AB_3B[DP_1X & !grepl("(^[1-9]+\\(3\\))|(3(-|X))", CLN$Event) & !grepl("(1|2)-3", CLN$Event)]
			
		# assign any runners that are still safe!
		TEM <- CLN$ID[DP_1X][str_count(CLN$Event[DP_1X], "-")==1]
		if (length(TEM) > 0) {
		
			for (tm in 1:length(TEM)) {
				
				# find the from and to bases
				rnnr <- sub(".*([B123]-[123H]).*", "\\1", CLN$Runners[CLN$ID==TEM[tm]])
				
				# assign the base via function 
				asgn_base(CLN, TEM[tm], rnnr)
			}
		}
      }
      # batter is safe, but both runners are out! #
      if (any(DP_2X)) {
            # 1B runner is out
            CLN$PE_1B[DP_2X & grepl("1X", CLN$Event)] <- NA
            # 1B runner safe and did not advance
            CLN$PE_1B[DP_2X & !grepl("1(-|X)", CLN$Event)] <- CLN$AB_1B[DP_2X & !grepl("1(-|X)", CLN$Event)]
            
            # 2B runner is out
            CLN$PE_2B[DP_2X & grepl("2(-|X)", CLN$Event)] <- NA
            # 2B runner safe and did not advance
            CLN$PE_2B[DP_1X & !grepl("2(-|X)", CLN$Event) & !grepl("1-", CLN$Event)] <- 
                  CLN$AB_2B[DP_1X & !grepl("2(-|X)", CLN$Event) & !grepl("1-", CLN$Event)]
            
            # 3B runenr is out
            CLN$PE_3B[DP_2X & grepl("3X", CLN$Event)] <- NA
            # 3B runner safe and did not advance
            CLN$PE_3B[DP_1X & !grepl("3(-|X)", CLN$Event) & !grepl("(1|2)-", CLN$Event)] <- 
                  CLN$AB_3B[DP_1X & !grepl("3(-|X)", CLN$Event & !grepl("(1|2)-", CLN$Event))]
            
            # batter is safe
            CLN$PE_1B[DP_2X] <- CLN$playerID[DP_2X]
		
		# assign any runners that are still safe!
		TEM <- CLN$ID[DP_2X][str_count(CLN$Event[DP_2X], "-")==1]
		if (length(TEM) > 0) {
		
			for (tm in 1:length(TEM)) {
				
				# find the from and to bases
				rnnr <- sub(".*([B123]-[123H]).*", "\\1", CLN$Runners[CLN$ID==TEM[tm]])
				
				# assign the base via function 
				asgn_base(CLN, TEM[tm], rnnr)
			}
		}
      }
      
      # # errors
      # CLN$PE_1B[E_B | E_1] <- CLN$playerID[E_B | E_1]
      # CLN$PE_2B[E_2] <- CLN$playerID[E_2]
      # CLN$PE_3B[E_3] <- CLN$playerID[E_3]
      
      # # WALK turned into double #
      # CLN$PE_2B[WK_2B] <- CLN$playerID[WK_2B]
      # CLN$PE_1B[WK_2B] <- NA # remove batter from 1st which is automatic from Walks above
	
      ## strikeout turned bad lol... ##
      CLN$PE_1B[grepl("^K.*BX1\\([1-9]*E[1-9]", CLN$Event)] <- 
            CLN$playerID[grepl("^K.*BX1\\([1-9]*E[1-9]", CLN$Event)]
      CLN$Outs[grepl("^K.*BX1\\([1-9]*E[1-9]", CLN$Event) & str_count(CLN$Event, "X") > 0] <-
            str_count(CLN$Event[grepl("^K.*BX1\\([1-9]*E[1-9]", CLN$Event) & str_count(CLN$Event, "X") > 0], "X")-1
      
      CLN$PE_2B[grepl("^K.*B-2", CLN$Event)] <- CLN$playerID[grepl("^K.*B-2", CLN$Event)]
      CLN$PE_3B[grepl("^K.*B-3", CLN$Event)] <- CLN$playerID[grepl("^K.*B-3", CLN$Event)]
      CLN$Outs[(grepl("^K.*B-3", CLN$Event) | grepl("^K.*B-2", CLN$Event))] <- 
            str_count(CLN$Event[(grepl("^K.*B-3", CLN$Event) | grepl("^K.*B-2", CLN$Event))], "X")
      
      ## ignore the change of inning inheriting of runners again, in case of any changes ##
      chg_inning <- data.table:::uniqlist(CLN[!is.na(CLN$Team),3:4])
      CLN$PE_1B[chg_inning-1] <- NA
      CLN$PE_2B[chg_inning-1] <- NA
      CLN$PE_3B[chg_inning-1] <- NA
      CLN$AB_1B[chg_inning] <- NA
      CLN$AB_2B[chg_inning] <- NA
      CLN$AB_3B[chg_inning] <- NA
      
      if (!isTRUE(all.equal(TMP, CLN))) {
            CLN <- adv_runnersNA(CLN)
      }
      return (CLN)
}

# divide and sort the data
dv_sort <- function(CLN) {
      
      ################################
      ##   Divide & Sort the Data   ## - BASIC
      ################################
      
      ## QUESTION: Just use ID column or include GP, Inning, Team, Outs, etc? Does it make sense?
      ##           - merging will be required if only use ID
      ##           - datasets will be huge and a lot of repeated material/information
      
      ## Hits ##
      # count runners -> 3 NAs = no runners #
      # 3-str_count(HT$Runners, "NA") #
      
      # Single
      Hit_tmp <- CLN[grepl("^S", CLN$Play) & !grepl("^(SB|SUB)", CLN$Play),]
      HT <- data.frame(ID=Hit_tmp$ID, GP=Hit_tmp$GP, Inning=Hit_tmp$Inning, Team=Hit_tmp$Team,
                       Outs=Hit_tmp$Outs, HitType="Single", 
                       Runners=3-str_count(paste(Hit_tmp$AB_1B, Hit_tmp$AB_2B, Hit_tmp$AB_3B, sep=";"), "NA"),
                       playerID=Hit_tmp$playerID, stringsAsFactors = FALSE)
      # Double
      Hit_tmp <- CLN[grepl("^D", CLN$Play),]
      HT <- rbind(HT, data.frame(ID=Hit_tmp$ID, GP=Hit_tmp$GP, Inning=Hit_tmp$Inning, Team=Hit_tmp$Team,
                                 Outs=Hit_tmp$Outs, HitType="Double", 
                                 Runners=3-str_count(paste(Hit_tmp$AB_1B, Hit_tmp$AB_2B, Hit_tmp$AB_3B, sep=";"), "NA"),
                                 playerID=Hit_tmp$playerID, stringsAsFactors = FALSE))
      # Triple
      Hit_tmp <- CLN[grepl("^T", CLN$Play),]
      HT <- rbind(HT, data.frame(ID=Hit_tmp$ID, GP=Hit_tmp$GP, Inning=Hit_tmp$Inning, Team=Hit_tmp$Team,
                                 Outs=Hit_tmp$Outs, HitType="Triple", 
                                 Runners=3-str_count(paste(Hit_tmp$AB_1B, Hit_tmp$AB_2B, Hit_tmp$AB_3B, sep=";"), "NA"),
                                 playerID=Hit_tmp$playerID, stringsAsFactors = FALSE))
      # HR
      Hit_tmp <- CLN[grepl("^HR", CLN$Play),]
      HT <- rbind(HT, data.frame(ID=Hit_tmp$ID, GP=Hit_tmp$GP, Inning=Hit_tmp$Inning, Team=Hit_tmp$Team,
                                 Outs=Hit_tmp$Outs, HitType="HR", 
                                 Runners=3-str_count(paste(Hit_tmp$AB_1B, Hit_tmp$AB_2B, Hit_tmp$AB_3B, sep=";"), "NA"),
                                 playerID=Hit_tmp$playerID, stringsAsFactors = FALSE))
      
      ## Walks & HP ##
      W_tmp <- CLN[grepl("^W", CLN$Play) & !grepl("WP", CLN$Play),]
      WK <- data.frame(ID=W_tmp$ID, GP=W_tmp$GP, Inning=W_tmp$Inning, Team=W_tmp$Team,
                       Outs=W_tmp$Outs, WType="Walk", 
                       Runners=3-str_count(paste(W_tmp$AB_1B, W_tmp$AB_2B, W_tmp$AB_3B, sep=";"), "NA"),
                       playerID=W_tmp$playerID, stringsAsFactors = FALSE)
      W_tmp <- CLN[grepl("^IW", CLN$Play),]
      WK <- rbind(WK, data.frame(ID=W_tmp$ID, GP=W_tmp$GP, Inning=W_tmp$Inning, Team=W_tmp$Team,
                                 Outs=W_tmp$Outs, WType="Int. Walk", 
                                 Runners=3-str_count(paste(W_tmp$AB_1B, W_tmp$AB_2B, W_tmp$AB_3B, sep=";"), "NA"),
                                 playerID=W_tmp$playerID, stringsAsFactors = FALSE))
      W_tmp <- CLN[grepl("^HP", CLN$Play),]
      WK <- rbind(WK, data.frame(ID=W_tmp$ID, GP=W_tmp$GP, Inning=W_tmp$Inning, Team=W_tmp$Team,
                                 Outs=W_tmp$Outs, WType="Hit By Pitch", 
                                 Runners=3-str_count(paste(W_tmp$AB_1B, W_tmp$AB_2B, W_tmp$AB_3B, sep=";"), "NA"),
                                 playerID=W_tmp$playerID, stringsAsFactors = FALSE))
      
      ## Strikeouts ##
      K_tmp <- CLN[grepl("^K", CLN$Play),]
      KS <- data.frame(ID=K_tmp$ID, GP=K_tmp$GP, Inning=K_tmp$Inning, Team=K_tmp$Team, Outs=K_tmp$Outs, 
                       Runners=3-str_count(paste(K_tmp$AB_1B, K_tmp$AB_2B, K_tmp$AB_3B, sep=";"), "NA"),
                       playerID=K_tmp$playerID, stringsAsFactors = FALSE)
      
      
      ## Stolen Bases ##
      # Stole 2B
      SB_tmp <- CLN[grepl("SB2", CLN$Play),]
      SB <- data.frame(ID=SB_tmp$ID, GP=SB_tmp$GP, Inning=SB_tmp$Inning, Team=SB_tmp$Team,
                       Outs=SB_tmp$Outs, playerID=SB_tmp$AB_1B, Base="2B", stringsAsFactors = FALSE)
      # Stole 3B
      SB_tmp <- CLN[grepl("SB3", CLN$Play),]
      SB <- rbind(SB, data.frame(ID=SB_tmp$ID, GP=SB_tmp$GP, Inning=SB_tmp$Inning, Team=SB_tmp$Team,
                                 Outs=SB_tmp$Outs, playerID=SB_tmp$AB_2B, Base="3B", stringsAsFactors = FALSE))
      # Stole Home
      SB_tmp <- CLN[grepl("SBH", CLN$Play),]
      SB <- rbind(SB, data.frame(ID=SB_tmp$ID, GP=SB_tmp$GP, Inning=SB_tmp$Inning, Team=SB_tmp$Team,
                                 Outs=SB_tmp$Outs, playerID=SB_tmp$AB_3B, Base="Home", stringsAsFactors = FALSE))
      
      ## Caught Stealing ##
      # Caught 2B
      CS_tmp <- CLN[grepl("CS2", CLN$Play),]
      CS <- data.frame(ID=CS_tmp$ID, GP=CS_tmp$GP, Inning=CS_tmp$Inning, Team=CS_tmp$Team,
                       Outs=CS_tmp$Outs, playerID=CS_tmp$AB_1B, Base="2B", stringsAsFactors = FALSE)
      
      # Caught 3B
      CS_tmp <- CLN[grepl("CS3", CLN$Play),]
      CS <- rbind(CS, data.frame(ID=CS_tmp$ID, GP=CS_tmp$GP, Inning=CS_tmp$Inning, Team=CS_tmp$Team,
                                 Outs=CS_tmp$Outs, playerID=CS_tmp$AB_2B, Base="3B", stringsAsFactors = FALSE))
      
      # Caught Home
      CS_tmp <- CLN[grepl("CSH", CLN$Play),]
      CS <- rbind(CS, data.frame(ID=CS_tmp$ID, GP=CS_tmp$GP, Inning=CS_tmp$Inning, Team=CS_tmp$Team,
                                 Outs=CS_tmp$Outs, playerID=CS_tmp$AB_3B, Base="Home", stringsAsFactors = FALSE))
      
      
      
      
      ## Aggregate and summarise by playerID & HitType ##
      HTS <- aggregate(ID ~ playerID + HitType, HT[HT$HitType=="Single",], length)
      HTD <- aggregate(ID ~ playerID + HitType, HT[HT$HitType=="Double",], length)
      HTT <- aggregate(ID ~ playerID + HitType, HT[HT$HitType=="Triple",], length)
      HTH <- aggregate(ID ~ playerID + HitType, HT[HT$HitType=="HR",], length)
      HT <- rename(merge(merge(rename(merge(HTS[!names(HTS) %in% "HitType"], HTD[!names(HTD) %in% "HitType"], 
                                            by="playerID", all=TRUE), c("ID.x"="singles", "ID.y"="doubles")), 
                               HTT[!names(HTT) %in% "HitType"], by="playerID", all=TRUE), 
                         HTH[!names(HTH) %in% "HitType"], by="playerID", all=TRUE), 
                   c("ID.x"="triples", "ID.y"="hr"))
      # HT[is.na(HT)] <- 0
      
      ## add in the rest SB, WK, K, CS
      HT <- merge(HT, rename(aggregate(ID ~ playerID, SB[names(SB) %in% c("ID", "playerID")], length),
                             c("ID"="sb")), by="playerID", all=TRUE)
      WKW <- aggregate(ID ~ playerID + WType, WK[WK$WType=="Walk",], length)
      WKI <- aggregate(ID ~ playerID + WType, WK[WK$WType=="Int. Walk",], length)
      WKH <- aggregate(ID ~ playerID + WType, WK[WK$WType=="Hit By Pitch",], length)
      HT <- merge(HT, rename(
            merge(WKH[!names(WKH) %in% "WType"], 
                  rename(merge(WKW[!names(WKW) %in% "WType"], WKI[!names(WKI) %in% "WType"], 
                               by="playerID", all=TRUE), c("ID.x"="w", "ID.y"="iw")), 
                  by="playerID", all=TRUE), c("ID"="hp")), by="playerID", all=TRUE)
      HT <- merge(HT, rename(aggregate(ID ~ playerID, KS[names(KS) %in% c("ID", "playerID")], length),
                             c("ID"="k")), by="playerID", all=TRUE)
      HT <- merge(HT, rename(aggregate(ID ~ playerID, CS[names(CS) %in% c("ID", "playerID")], length),
                             c("ID"="cs")), by="playerID", all=TRUE)
      # HT[is.na(HT)] <- 0
      
      # types of balls in play
      # bip <- unique(CLN$Play[!grepl("^(FLE|PO|CS|SB|WP|HP|IW|W|OA|PB|BK|SUB|NP)", CLN$Play)])
      # bip <- bip[order(bip)]
      
      # plate appearances: incl. walks, errors, sac flies, etc.
      PA <- CLN[!grepl("^(FLE|PO|CS|SB|WP|OA|PB|BK|SUB|NP)", CLN$Play),]
      HT <- merge(HT, rename(aggregate(ID ~ playerID, PA[names(PA) %in% c("ID", "playerID")], length),
                             c("ID"="pa")), by="playerID", all=TRUE)
      
      # at-bats: exclude walks, sac flies, sac hits
      AB <- PA[!grepl("^(W|IW|HP)", PA$Play) & !grepl("/(SF|SH)", PA$Event),]
      HT <- merge(HT, rename(aggregate(ID ~ playerID, AB[names(AB) %in% c("ID", "playerID")], length),
                             c("ID"="ab")), by="playerID", all=TRUE)
      # sac hits/flies
      SH <- PA[grepl("/(SF|SH)", PA$Event),]
      HT <- merge(HT, rename(aggregate(ID ~ playerID, SH[names(SH) %in% c("ID", "playerID")], length),
                             c("ID"="sh")), by="playerID", all=TRUE)
      
      HT[is.na(HT)] <- 0
      
      # total hits
      HT$hits <- HT$singles+HT$doubles+HT$triples+HT$hr
      
      
      # rearrange columns
      HT <- HT[,c("playerID", "pa", "ab", "hits", "singles", "doubles", "triples", "hr", 
                  "w", "iw", "hp", "k", "sh", "sb", "cs")]
      
      # done. most basic stats :D
      
      # output as a list
      return(list(CLN, HT))
}

################################
################################


################################
##     Parse All Gamelogs     ##
################################

# simple set up, read. scan for line headers
setwd("~/Personal/Practice/MLB")
# setwd("~/Data-4fun/Baseball")
# EVN <- readLines("C:/Users/siling/Desktop/DoesNotNeedContinuousBackup/2010seve/2016TOR.EVA")
# CWS stadium had 3 triple plays in 2016.
# EVN <- readLines("C:/Users/siling/Desktop/DoesNotNeedContinuousBackup/2010seve/2016CHA.EVA") 

# put all 2016 events together
# evn2016 <- list.files("Gamelogs")
work_loc <- "C:/Users/siling/Desktop/DoesNotNeedContinuousBackup/2010seve"
evn2016 <- list.files(work_loc)
evn2016 <- evn2016[grepl("^2016", evn2016)]
BasicStats <- NULL # set the final output
IntmdStats <- NULL # set the final output
EVN <- NULL # all events

# combine all lines from events
for (e in 1:length(evn2016)) {
	
	# loop thru to collect all lines from all 2016 events
	ENS <- readLines(paste(work_loc, evn2016[e], sep="/"))
	EVN <- c(EVN, ENS)
}

# parse for initial setup state #
T1 <- Sys.time()
CLN <- init_state(EVN, posis)
T2 <- Sys.time()
message("Initial Setup:"); print(T2-T1)

# recursively assign outs #
all_plyExcp1st <- 2:nrow(CLN)
chg_inning <- data.table:::uniqlist(CLN[!is.na(CLN$Team),3:4])
T1 <- Sys.time()
CLN <- asgn_outs(CLN, all_plyExcp1st, chg_inning)
T2 <- Sys.time()
message("Assign Outs:"); print(T2-T1)

# run the recursive function to move / remove runners #
T1 <- Sys.time()
CLN <- adv_runnersNA(CLN)
T2 <- Sys.time()
message("Advance Runners:"); print(T2-T1)

message("2016 completed!")
x <- c(nrow(CLN[grepl("1(-|X)", CLN$Runners) & is.na(CLN$AB_1B),]),
       nrow(CLN[grepl("2(-|X)", CLN$Runners) & is.na(CLN$AB_2B),]),
       nrow(CLN[grepl("3(-|X)", CLN$Runners) & is.na(CLN$AB_3B),]),
       nrow(CLN[compareNA(CLN$AB_1B, CLN$AB_2B) & !is.na(CLN$AB_1B),]),
       nrow(CLN[compareNA(CLN$AB_1B, CLN$AB_2B) & !is.na(CLN$AB_2B),]),
       nrow(CLN[compareNA(CLN$AB_2B, CLN$AB_3B) & !is.na(CLN$AB_2B),]),
       nrow(CLN[compareNA(CLN$AB_2B, CLN$AB_3B) & !is.na(CLN$AB_3B),]),
       nrow(CLN[compareNA(CLN$PE_1B, CLN$PE_2B) & !is.na(CLN$PE_1B),]),
       nrow(CLN[compareNA(CLN$PE_1B, CLN$PE_2B) & !is.na(CLN$PE_2B),]),
       nrow(CLN[compareNA(CLN$PE_2B, CLN$PE_3B) & !is.na(CLN$PE_3B),]),
       nrow(CLN[compareNA(CLN$PE_1B, CLN$PE_2B) & !is.na(CLN$PE_1B),]),
       nrow(CLN[compareNA(CLN$PE_2B, CLN$PE_3B) & !is.na(CLN$PE_2B),]),
       nrow(CLN[compareNA(CLN$PE_2B, CLN$PE_3B) & !is.na(CLN$PE_3B),]))
print(x)
message(paste("Total errors:", sum(x)))

################################
################################


################################
##   Divide & Sort the Data   ## - INTERMEDIATE ?
################################



################################
################################

### Perform Checks - for next couple versions ###

# checks 2010-2015
pb <- txtProgressBar(min = 2010, max = 2015, style=3)
for (y in 2010:2015) {
      
      message(paste("Year:", y))
      # parse the event file
      TS <- Sys.time()
      evn2010s <- list.files(work_loc)
      use_yr <- paste0("^", y)
      evn2010s <- evn2010s[grepl(use_yr, evn2010s)]
      BasicStats <- NULL # set the final output
      IntmdStats <- NULL # set the final output
      EVN <- NULL # all events
      
      # combine all lines from events
      for (e in 1:length(evn2010s)) {
            
            # loop thru to collect all lines from each year's events
            ENS <- readLines(paste(work_loc, evn2010s[e], sep="/"))
            EVN <- c(EVN, ENS)
      }
      
      # parse for initial setup state #
      T1 <- Sys.time()
      CLN <- init_state(EVN, posis)
      T2 <- Sys.time()
      message("Initial Setup:"); print(T2-T1)
      
      # recursively assign outs #
      all_plyExcp1st <- 2:nrow(CLN)
      chg_inning <- data.table:::uniqlist(CLN[!is.na(CLN$Team),3:4])
      T1 <- Sys.time()
      CLN <- asgn_outs(CLN, all_plyExcp1st, chg_inning)
      T2 <- Sys.time()
      message("Assign Outs:"); print(T2-T1)
      
      # run the recursive function to move / remove runners #
      T1 <- Sys.time()
      CLN <- adv_runnersNA(CLN)
      T2 <- Sys.time()
      message("Advance Runners:"); print(T2-T1)
      
      # error checks
      x <- c(nrow(CLN[grepl("1(-|X)", CLN$Runners) & is.na(CLN$AB_1B),]),
             nrow(CLN[grepl("2(-|X)", CLN$Runners) & is.na(CLN$AB_2B),]),
             nrow(CLN[grepl("3(-|X)", CLN$Runners) & is.na(CLN$AB_3B),]),
             nrow(CLN[compareNA(CLN$AB_1B, CLN$AB_2B) & !is.na(CLN$AB_1B),]),
             nrow(CLN[compareNA(CLN$AB_1B, CLN$AB_2B) & !is.na(CLN$AB_2B),]),
             nrow(CLN[compareNA(CLN$AB_2B, CLN$AB_3B) & !is.na(CLN$AB_2B),]),
             nrow(CLN[compareNA(CLN$AB_2B, CLN$AB_3B) & !is.na(CLN$AB_3B),]),
             nrow(CLN[compareNA(CLN$PE_1B, CLN$PE_2B) & !is.na(CLN$PE_1B),]),
             nrow(CLN[compareNA(CLN$PE_1B, CLN$PE_2B) & !is.na(CLN$PE_2B),]),
             nrow(CLN[compareNA(CLN$PE_2B, CLN$PE_3B) & !is.na(CLN$PE_3B),]),
             nrow(CLN[compareNA(CLN$PE_1B, CLN$PE_2B) & !is.na(CLN$PE_1B),]),
             nrow(CLN[compareNA(CLN$PE_2B, CLN$PE_3B) & !is.na(CLN$PE_2B),]),
             nrow(CLN[compareNA(CLN$PE_2B, CLN$PE_3B) & !is.na(CLN$PE_3B),]))
      if (any(x > 0) | !length(count(CLN$PE_Outs)$x)==4) {
            eval(parse(text=paste0("ERR",y, " <- CLN")))
      }
      
      message(paste(y, "completed!"))
      print(x)
      message(paste("Total errors:", sum(x)))
      setTxtProgressBar(pb, y)
}

# checks 2000-2009
pb <- txtProgressBar(min=2000, max=2009, style=3)
for (y in 2000:2009) {
      
      # parse the event file
      TS <- Sys.time()
      work_loc <- "C:/Users/siling/Desktop/DoesNotNeedContinuousBackup/2000seve"
      evn2000s <- list.files(work_loc)
      use_yr <- paste0("^", y)
      evn2000s <- evn2000s[grepl(use_yr, evn2000s)]
      BasicStats <- NULL # set the final output
      IntmdStats <- NULL # set the final output
      EVN <- NULL # all events
      
      # combine all lines from events
      for (e in 1:length(evn2000s)) {
            
            # loop thru to collect all lines from each year's events
            ENS <- readLines(paste(work_loc, evn2000s[e], sep="/"))
            EVN <- c(EVN, ENS)
      }
      
      TM <- Sys.time()
      OUTPUT <- basic_stats(EVN, posis)
      CLN <- OUTPUT[[1]]
      TE <- Sys.time()
      message("Initial Load:")
      print(TM-TS)
      message("Processing:")
      print(TE-TM)
      
      # error checks
      x <- c(nrow(CLN[grepl("1(-|X)", CLN$Runners) & is.na(CLN$AB_1B),]),
             nrow(CLN[grepl("2(-|X)", CLN$Runners) & is.na(CLN$AB_2B),]),
             nrow(CLN[grepl("3(-|X)", CLN$Runners) & is.na(CLN$AB_3B),]),
             nrow(CLN[compareNA(CLN$AB_1B, CLN$AB_2B) & !is.na(CLN$AB_1B),]),
             nrow(CLN[compareNA(CLN$AB_1B, CLN$AB_2B) & !is.na(CLN$AB_2B),]),
             nrow(CLN[compareNA(CLN$AB_2B, CLN$AB_3B) & !is.na(CLN$AB_2B),]),
             nrow(CLN[compareNA(CLN$AB_2B, CLN$AB_3B) & !is.na(CLN$AB_3B),]),
             nrow(CLN[compareNA(CLN$PE_1B, CLN$PE_2B) & !is.na(CLN$PE_1B),]),
             nrow(CLN[compareNA(CLN$PE_1B, CLN$PE_2B) & !is.na(CLN$PE_2B),]),
             nrow(CLN[compareNA(CLN$PE_2B, CLN$PE_3B) & !is.na(CLN$PE_3B),]),
             nrow(CLN[compareNA(CLN$PE_1B, CLN$PE_2B) & !is.na(CLN$PE_1B),]),
             nrow(CLN[compareNA(CLN$PE_2B, CLN$PE_3B) & !is.na(CLN$PE_2B),]),
             nrow(CLN[compareNA(CLN$PE_2B, CLN$PE_3B) & !is.na(CLN$PE_3B),]))
      if (any(x > 0) | !length(count(CLN$PE_Outs)$x)==4) {
            eval(parse(text=paste0("ERR",y, " <- CLN")))
      }
      
      setTxtProgressBar(pb, y)
      message(paste(y, "completed!"))
}

# checks 1990-1999
pb <- txtProgressBar(min=1990, max=1999, style=3)
for (y in 1990:1999) {
      
      # parse the event file
      TS <- Sys.time()
      work_loc <- "C:/Users/siling/Desktop/DoesNotNeedContinuousBackup/1990seve"
      evn1990s <- list.files(work_loc)
      use_yr <- paste0("^", y)
      evn1990s <- evn1990s[grepl(use_yr, evn1990s)]
      BasicStats <- NULL # set the final output
      IntmdStats <- NULL # set the final output
      EVN <- NULL # all events
      
      # combine all lines from events
      for (e in 1:length(evn1990s)) {
            
            # loop thru to collect all lines from each year's events
            ENS <- readLines(paste(work_loc, evn1990s[e], sep="/"))
            EVN <- c(EVN, ENS)
      }
      
      TM <- Sys.time()
      OUTPUT <- basic_stats(EVN, posis)
      CLN <- OUTPUT[[1]]
      TE <- Sys.time()
      message("Initial Load:")
      print(TM-TS)
      message("Processing:")
      print(TE-TM)
      
      # error checks
      x <- c(nrow(CLN[grepl("1(-|X)", CLN$Runners) & is.na(CLN$AB_1B),]),
             nrow(CLN[grepl("2(-|X)", CLN$Runners) & is.na(CLN$AB_2B),]),
             nrow(CLN[grepl("3(-|X)", CLN$Runners) & is.na(CLN$AB_3B),]),
             nrow(CLN[compareNA(CLN$AB_1B, CLN$AB_2B) & !is.na(CLN$AB_1B),]),
             nrow(CLN[compareNA(CLN$AB_1B, CLN$AB_2B) & !is.na(CLN$AB_2B),]),
             nrow(CLN[compareNA(CLN$AB_2B, CLN$AB_3B) & !is.na(CLN$AB_2B),]),
             nrow(CLN[compareNA(CLN$AB_2B, CLN$AB_3B) & !is.na(CLN$AB_3B),]),
             nrow(CLN[compareNA(CLN$PE_1B, CLN$PE_2B) & !is.na(CLN$PE_1B),]),
             nrow(CLN[compareNA(CLN$PE_1B, CLN$PE_2B) & !is.na(CLN$PE_2B),]),
             nrow(CLN[compareNA(CLN$PE_2B, CLN$PE_3B) & !is.na(CLN$PE_3B),]),
             nrow(CLN[compareNA(CLN$PE_1B, CLN$PE_2B) & !is.na(CLN$PE_1B),]),
             nrow(CLN[compareNA(CLN$PE_2B, CLN$PE_3B) & !is.na(CLN$PE_2B),]),
             nrow(CLN[compareNA(CLN$PE_2B, CLN$PE_3B) & !is.na(CLN$PE_3B),]))
      if (any(x > 0) | !length(count(CLN$PE_Outs)$x)==4) {
            eval(parse(text=paste0("ERR",y, " <- CLN")))
      }
      
      setTxtProgressBar(pb, y)
      message(paste(y, "completed!"))
}









#
# - more than 3 outs - just filter
      count(CLN$PE_Outs)
      View(CLN[CLN$PE_Outs > 3,])
      # === DONE === 2010-2016 - version 1.2.7
      # == PENDING == < 2009 - version 1.2.7
#
# - runner advance/remove but no original runner! GHOST RUNNER LOL
#     - ex) View(CLN[grepl("1(-|X)", CLN$Runners) & is.na(CLN$AB_1B),])
#     - ex) test01 <- 2016222164
#           View(CLN[CLN$ID %in% c(test01:(test01-10),test01:(test01+9)),])
      View(CLN[grepl("1(-|X)", CLN$Runners) & is.na(CLN$AB_1B),])
      View(CLN[grepl("2(-|X)", CLN$Runners) & is.na(CLN$AB_2B),])
      View(CLN[grepl("3(-|X)", CLN$Runners) & is.na(CLN$AB_3B),])
      nrow(CLN[grepl("1(-|X)", CLN$Runners) & is.na(CLN$AB_1B),])
      nrow(CLN[grepl("2(-|X)", CLN$Runners) & is.na(CLN$AB_2B),])
      nrow(CLN[grepl("3(-|X)", CLN$Runners) & is.na(CLN$AB_3B),])
      # === DONE === 2010-2016 - version 1.2.7
      # == PENDING == < 2009 - version 1.2.7
# - duplicate runners check lol
      View(CLN[compareNA(CLN$AB_1B, CLN$AB_2B) & !is.na(CLN$AB_1B),])
      View(CLN[compareNA(CLN$AB_1B, CLN$AB_2B) & !is.na(CLN$AB_2B),])
      View(CLN[compareNA(CLN$AB_2B, CLN$AB_3B) & !is.na(CLN$AB_2B),])
      View(CLN[compareNA(CLN$AB_2B, CLN$AB_3B) & !is.na(CLN$AB_3B),])
      View(CLN[compareNA(CLN$PE_1B, CLN$PE_2B) & !is.na(CLN$PE_1B),])
      View(CLN[compareNA(CLN$PE_1B, CLN$PE_2B) & !is.na(CLN$PE_2B),])
      View(CLN[compareNA(CLN$PE_2B, CLN$PE_3B) & !is.na(CLN$PE_3B),])
      View(CLN[compareNA(CLN$PE_1B, CLN$PE_2B) & !is.na(CLN$PE_1B),])
      View(CLN[compareNA(CLN$PE_2B, CLN$PE_3B) & !is.na(CLN$PE_2B),])
      View(CLN[compareNA(CLN$PE_2B, CLN$PE_3B) & !is.na(CLN$PE_3B),])
      nrow(CLN[compareNA(CLN$AB_1B, CLN$AB_2B) & !is.na(CLN$AB_1B),])
      nrow(CLN[compareNA(CLN$AB_1B, CLN$AB_2B) & !is.na(CLN$AB_2B),])
      nrow(CLN[compareNA(CLN$AB_2B, CLN$AB_3B) & !is.na(CLN$AB_2B),])
      nrow(CLN[compareNA(CLN$AB_2B, CLN$AB_3B) & !is.na(CLN$AB_3B),])
      nrow(CLN[compareNA(CLN$PE_1B, CLN$PE_2B) & !is.na(CLN$PE_1B),])
      nrow(CLN[compareNA(CLN$PE_1B, CLN$PE_2B) & !is.na(CLN$PE_2B),])
      nrow(CLN[compareNA(CLN$PE_2B, CLN$PE_3B) & !is.na(CLN$PE_3B),])
      nrow(CLN[compareNA(CLN$PE_1B, CLN$PE_2B) & !is.na(CLN$PE_1B),])
      nrow(CLN[compareNA(CLN$PE_2B, CLN$PE_3B) & !is.na(CLN$PE_2B),])
      nrow(CLN[compareNA(CLN$PE_2B, CLN$PE_3B) & !is.na(CLN$PE_3B),])
      # === DONE === 2010-2016 - version 1.2.7
      # == PENDING == < 2009 - version 1.2.7
# - final scores 










