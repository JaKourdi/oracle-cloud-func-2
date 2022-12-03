import io
import json
import logging

import oci
from fdk import response

def handler(ctx, data: io.BytesIO=None):
    if None == ctx.RequestURL():
        return "Function loaded properly but not invoked via an HTTP request."
    signer = oci.auth.signers.get_resource_principals_signer()
    logging.getLogger().info("URI: " + ctx.RequestURL() )
    config = {
        "tenancy": "ocid1.tenancy.oc1..aaaaaaaat3g6mubuxwcl26ef5tve3gpoz3bnrueskq7ma2fyjlk3jiiinxea",
        "region": "il-jerusalem-1"
    }
    if ctx.Method() == "GET":
        try:
            object_storage = oci.object_storage.ObjectStorageClient(config, signer=signer)
            namespace = object_storage.get_namespace().data
            # update with your bucket name
            bucket_name = "assignment1"
            file_object_name = ctx.RequestURL()
            if file_object_name.endswith("/"):
                logging.getLogger().info("Adding index.html to request URL " + file_object_name)
                file_object_name += "index.html"

            # strip off the first character of the URI (i.e. the /)
            file_object_name = file_object_name[1:]

            obj = object_storage.get_object(namespace, bucket_name, file_object_name)
            return response.Response(
                ctx, response_data=obj.data.content,
                headers={"Content-Type": obj.headers['Content-type']}
            )
        except (Exception) as e:
            return response.Response(
                ctx, response_data="500 Server error",
                headers={"Content-Type": "text/plain"}
            )
    else:
        return response.Response(
            ctx, response_data="405  Method not allowed",
            headers={"Content-Type": "text/plain"},
            status_code=405
        )