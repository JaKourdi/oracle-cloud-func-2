import io
import json
import logging
import csv

import oci
from fdk import response

# create, read, update, and delete (CRUD)
allowed_endpoint = ['', 'read', 'create', 'update', 'delete', 'listall']


def handler(ctx, data: io.BytesIO = None):
    if None == ctx.RequestURL():
        return "Function loaded properly but not invoked via an HTTP request."
    signer = oci.auth.signers.get_resource_principals_signer()
    logging.getLogger().info("URI: " + ctx.RequestURL())
    config = {
        "tenancy": "ocid1.tenancy.oc1..aaaaaaaat3g6mubuxwcl26ef5tve3gpoz3bnrueskq7ma2fyjlk3jiiinxea",
        "region": "il-jerusalem-1"
    }
    object_storage = oci.object_storage.ObjectStorageClient(config, signer=signer)
    namespace = object_storage.get_namespace().data
    bucket_name = "assignment2"
    file_object_name = ctx.RequestURL()
    if ctx.Method() == "GET":
        try:
            object_storage = oci.object_storage.ObjectStorageClient(config, signer=signer)
            namespace = object_storage.get_namespace().data
            # update with your bucket name
            bucket_name = "assignment2"
            file_object_name = ctx.RequestURL()
            if file_object_name.endswith("/"):
                obj = object_storage.get_object(namespace, bucket_name, 'index.html')
                return response.Response(
                    ctx, response_data=obj.data.content,
                    headers={"Content-Type": obj.headers['Content-type']}
                )
            elif file_object_name.endswith("/getcsv"):
                obj = object_storage.get_object(namespace, bucket_name, 'db.csv')
                return response.Response(
                    ctx, response_data=obj.data.content,
                    headers={"Content-Type": obj.headers['Content-type']}
                )
            else:
                error_500(ctx)
        except (Exception) as e:
            error_500(ctx)
    elif ctx.Method() == "POST":
        obj = object_storage.get_object(namespace, bucket_name, 'csv.html')
        try:
            body = json.loads(data.getvalue())
            name = body.get("name")
        except (Exception, ValueError) as ex:
            print(str(ex))
        return response.Response(
            ctx, response_data=json.dumps(
                {"Message": "Hello {0}".format(name),
                 "ctx.Config" : dict(ctx.Config()),
                 "ctx.Headers" : ctx.Headers(),
                 "ctx.AppID" : ctx.AppID(),
                 "ctx.FnID" : ctx.FnID(),
                 "ctx.CallID" : ctx.CallID(),
                 "ctx.Format" : ctx.Format(),
                 "ctx.Deadline" : ctx.Deadline(),
                 "ctx.RequestURL": ctx.RequestURL(),
                 "ctx.Method": ctx.Method()},
                sort_keys=True, indent=4),
            headers={"Content-Type": "application/json"}
)

    else:
        return response.Response(
            ctx, response_data="405  Method not allowed",
            headers={"Content-Type": "text/plain"},
            status_code=405
        )


def error_500(ctx):
    return response.Response(
        ctx, response_data="500 Server error",
        headers={"Content-Type": "text/plain"}
    )


# POST– This creates a new record in the database.
# GET– This request reads information sourced from a database.
# PUT– This updates an object.
# DELETE– This removes a record from the database.

def new_record():
    return
def read_record():
    return
def update_record():
    return
def delete_record():
    return


def route(ctx):
    m_method = ctx.Method()
    if m_method == 'GET':
        return
    elif m_method == 'POST':
        return
    elif m_method == 'PUT':
        return
    elif m_method == 'DELETE':
        return
    else:
        return error_500(ctx)



def route(endpoint):
    return


def redirect(ctx):
    m_method = ctx.Method()
    if m_method == 'GET':
        return
    elif m_method == 'POST':
        return
    elif m_method == 'PUT':
        return
    elif m_method == 'DELETE':
        return
    else:
        return error_500(ctx)