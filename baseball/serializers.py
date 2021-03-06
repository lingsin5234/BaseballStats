from rest_framework import serializers


# batting
class BatStatSerializer(serializers.Serializer):
    NAME = serializers.CharField()
    TEAM = serializers.CharField()
    GP = serializers.IntegerField()
    GS = serializers.IntegerField()
    AB = serializers.IntegerField()
    PA = serializers.IntegerField()
    H = serializers.IntegerField()
    D = serializers.IntegerField()
    T = serializers.IntegerField()
    HR = serializers.IntegerField()
    RBI = serializers.IntegerField()
    R = serializers.IntegerField()
    BB = serializers.IntegerField()
    IW = serializers.IntegerField()
    K = serializers.IntegerField()
    SB = serializers.IntegerField()
    CS = serializers.IntegerField()
    LOB = serializers.IntegerField()
    RLSP = serializers.IntegerField()
    GDP = serializers.IntegerField()
    HBP = serializers.IntegerField()
    SH = serializers.IntegerField()
    SF = serializers.IntegerField()
    PH = serializers.IntegerField()
    PR = serializers.IntegerField()


# pitching
class PitchStatSerializer(serializers.Serializer):
    NAME = serializers.CharField()
    TEAM = serializers.CharField()
    GP = serializers.IntegerField()
    GS = serializers.IntegerField()
    IP = serializers.IntegerField()
    BF = serializers.IntegerField()
    # W = serializers.IntegerField()
    # L = serializers.IntegerField()
    # HD = serializers.IntegerField()
    # SV = serializers.IntegerField()
    R = serializers.IntegerField()
    ER = serializers.IntegerField()
    H = serializers.IntegerField()
    HR = serializers.IntegerField()
    K = serializers.IntegerField()
    BB = serializers.IntegerField()
    IBB = serializers.IntegerField()
    HBP = serializers.IntegerField()
    POA = serializers.IntegerField()
    PO = serializers.IntegerField()
    WP = serializers.IntegerField()
    PB = serializers.IntegerField()
    BK = serializers.IntegerField()
    DI = serializers.IntegerField()
    CI = serializers.IntegerField()
    PT = serializers.IntegerField()
    ST = serializers.IntegerField()
    BT = serializers.IntegerField()
    FL = serializers.IntegerField()
    

# fielding
class FieldStatSerializer(serializers.Serializer):
    NAME = serializers.CharField()
    TEAM = serializers.CharField()
    GP = serializers.IntegerField()
    GS = serializers.IntegerField()
    IP = serializers.IntegerField()
    # BF = serializers.IntegerField()
    # W = serializers.IntegerField()
    # L = serializers.IntegerField()
    # HD = serializers.IntegerField()
    # SV = serializers.IntegerField()
    # R = serializers.IntegerField()
    # ER = serializers.IntegerField()
    A = serializers.IntegerField()
    PO = serializers.IntegerField()
    DP = serializers.IntegerField()
    TP = serializers.IntegerField()
    E = serializers.IntegerField()
