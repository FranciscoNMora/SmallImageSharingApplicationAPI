from rest_framework import serializers

from PostsApp.app_utils.general_utils import unix_timestamp


class UnixTimestampField(serializers.Field):
    """
    required for converting Datetime to Int unix timestamps
    """
    def to_representation(self, value):
        return unix_timestamp(value)