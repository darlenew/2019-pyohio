import os

from google.cloud import storage


class GCSBucket:

    def __init__(self, json_service_key_path, bucket_name):
        self.json_service_key_path = os.path.expanduser(json_service_key_path)
        self.bucket_name = bucket_name

        self._bucket = None

    @property
    def bucket(self):
        if not self._bucket:
            storage_client = storage.Client.from_service_account_json(
                self.json_service_key_path)
            self._bucket = storage_client.get_bucket(self.bucket_name)

        return self._bucket


    def upload(self, src, dst, **metadata):
        """Upload local file to dst in GCS bucket along with metadata.
        Args:
            src: path to local file
            dst: target GCS name for the blob object
            metadata: custom metadata to associate with the blob

        Example:
        >>> json_service_key = 'my-service-key.json'
        >>> bucket_name = 'my-bucket-name'
        >>> b = GCSBucket(json_service_key, bucket_name)
        >>> b.upload('/tmp/foo', 'foobar', count=5, finished="yes")
        """
        blob = self.bucket.blob(dst)
        blob.metadata = metadata
        blob.upload_from_filename(src)
