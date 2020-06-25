from rest_framework import serializers


class StatSerializer(serializers.Serializer):
    # Your data serializer, define your fields here.
    # results = serializers.ListField()
    # heading = serializers.CharField()
    # post_col = serializers.ListField()
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

