from rest_framework import serializers


class StatSerializer(serializers.Serializer):
    # Your data serializer, define your fields here.
    results = serializers.ListField()
    heading = serializers.CharField()
    post_col = serializers.ListField()
