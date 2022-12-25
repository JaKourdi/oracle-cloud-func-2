import io
import json
import logging
import csv
import pandas as pd

import oci
from fdk import response

# create, read, update, and delete (CRUD)
allowed_endpoint = ['', 'read', 'create', 'update', 'delete', 'listall']
csv_api_url = "https://m7l2i2ximv4pqfi3xlea5yb53u.apigateway.il-jerusalem-1.oci.customer-oci.com/app2/getcsv"

config = {
    "tenancy": "ocid1.tenancy.oc1..aaaaaaaat3g6mubuxwcl26ef5tve3gpoz3bnrueskq7ma2fyjlk3jiiinxea",
    "region": "il-jerusalem-1"
}
signer = oci.auth.signers.get_resource_principals_signer()
object_storage = oci.object_storage.ObjectStorageClient(config, signer=signer)
namespace = object_storage.get_namespace().data
bucket_name = "assignment2"


def handler(ctx, data: io.BytesIO = None):
    if None == ctx.RequestURL():
        return "Function loaded properly but not invoked via an HTTP request."
    signer = oci.auth.signers.get_resource_principals_signer()
    logging.getLogger().info("URI: " + ctx.RequestURL())
    config = {
        "tenancy": "ocid1.tenancy.oc1..aaaaaaaat3g6mubuxwcl26ef5tve3gpoz3bnrueskq7ma2fyjlk3jiiinxea",
        "region": "il-jerusalem-1"
    }
    if ctx.Method() == "GET":
        try:
            endpoint = ctx.RequestURL()
            if endpoint.endswith("/"):
                obj = object_storage.get_object(namespace, bucket_name, 'index.html')
                return response.Response(
                    ctx, response_data=obj.data.content,
                    headers={"Content-Type": obj.headers['Content-type']}
                )
            elif endpoint.endswith("/getcsv"):
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
        # obj = object_storage.get_object(namespace, bucket_name, 'csv.html')
        new_record(ctx, data)

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

def new_record(ctx, data):
    try:
        body = json.loads(data.getvalue())
        name = body.get("name")
        department = body.get("department")
        birthday = body.get("birthday")
        df = pd.read_csv(csv_api_url)
        new_row = {'name': name, 'department': department, 'birthday': birthday}
        df2 = df.append(new_row, ignore_index=True)
        df2.to_csv()
        object_storage.put_object(namespace, bucket_name, 'db.csv', df2.to_csv())
        return response.Response(
            ctx, response_data=json.dumps(
                {"Message": "Hello {0}, you work at {1} and your birthday is {2} - Bucket updated".format(name,
                                                                                                          department,
                                                                                                          birthday),
                 "csv": df.to_string(),
                 "ctx.Config": dict(ctx.Config()),
                 "ctx.Headers": ctx.Headers(),
                 "ctx.AppID": ctx.AppID(),
                 "ctx.FnID": ctx.FnID(),
                 "ctx.CallID": ctx.CallID(),
                 "ctx.Format": ctx.Format(),
                 "ctx.Deadline": ctx.Deadline(),
                 "ctx.RequestURL": ctx.RequestURL(),
                 "ctx.Method": ctx.Method()},
                sort_keys=True, indent=4),
            headers={"Content-Type": "application/json"}
        )
    except (Exception, ValueError) as ex:
        error_500(ctx)


def read_record():
    return


def update_record(ctx, data):
    try:
        body = json.loads(data.getvalue())
        name = body.get("name")
        department = body.get("department")
        birthday = body.get("birthday")
        df = pd.read_csv(csv_api_url)

        if not check_if_name_exist(df, name):
            return response.Response(
                ctx, response_data="404 Person not found! try a diff name",
                headers={"Content-Type": "text/plain"}
            )
        else:
            df.loc[df.name == "John Smith", 'department'] = department
            df.loc[df.birthday == "John Smith", 'birthday'] = birthday
            df.loc[df.name == name, 'name'] = name
            # Update object store.
            object_storage.put_object(namespace, bucket_name, 'db.csv', df.to_csv())
            return response.Response(
                ctx, response_data=json.dumps(
                    {
                        "Message": "Updated: {0}, work is now {1} and his birthday is {2} - Updated contact details.".format(
                            name, department, birthday),
                        "csv": df.to_string(),
                        "ctx.Config": dict(ctx.Config()),
                        "ctx.Headers": ctx.Headers(),
                        "ctx.AppID": ctx.AppID(),
                        "ctx.FnID": ctx.FnID(),
                        "ctx.CallID": ctx.CallID(),
                        "ctx.Format": ctx.Format(),
                        "ctx.Deadline": ctx.Deadline(),
                        "ctx.RequestURL": ctx.RequestURL(),
                        "ctx.Method": ctx.Method()},
                    sort_keys=True, indent=4),
                headers={"Content-Type": "application/json"}
            )
    except (Exception, ValueError) as ex:
        error_500(ctx)


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


def check_if_name_exist(df, name):
    if df['name'].isin([name]).any():
        return False
    return True
