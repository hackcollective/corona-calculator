import pickle

from data.utils import download_data, upload_data_to_s3

if __name__ == "__main__":
    data_object = download_data()
    pickle_byte_obj = pickle.dumps(data_object)
    success = upload_data_to_s3(pickle_byte_obj)

    if success:
        print(f"Results pushed to S3.")
    else:
        print("Push to S3 failed. Do you have the correct credentials?")
