import io
import json
import logging
import csv
import pandas as pd

import oci
from fdk import response


def check_if_name_exist(df, name):
    if df['name'].isin([name]).any():
        return False
    return True


# create, read, update, and delete (CRUD)
allowed_endpoint = ['', 'read', 'create', 'update', 'delete', 'listall']
csv_api_url = "https://objectstorage.il-jerusalem-1.oraclecloud.com/n/axr8cosciqjx/b/assignment2/o/db.csv"

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
                df = pd.read_csv(csv_api_url)
                return response.Response(
                    ctx, response_data=json.dumps(
                        {"Message": "Hello",
                         "csv": df.to_string()}, sort_keys=True, indent=4),
                    headers={"Content-Type": "application/json"})
            else:
                error_500(ctx)
        except (Exception) as e:
            error_500(ctx)
    elif ctx.Method() == "POST":
        # obj = object_storage.get_object(namespace, bucket_name, 'csv.html')
        new_record(ctx, data)

    elif ctx.Method() == "PUT":
        update_record(ctx, data)

    elif ctx.Method == "DELETE":
        delete_record(ctx)


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


# POST??? This creates a new record in the database.
# GET??? This request reads information sourced from a database.
# PUT??? This updates an object.
# DELETE??? This removes a record from the database.

def new_record(ctx, data):
    try:
        name, department, birthday = read_data(data)
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


def read_record(ctx):
    name = "John Smith"
    df = pd.read_csv(csv_api_url)
    if not check_if_name_exist(df, name):
        return response.Response(
            ctx, response_data="404 Person not found! try a diff name",
            headers={"Content-Type": "text/plain"})
    return response.Response(
        ctx, response_data=json.dumps(
            {"Message": "You found me",
             "name": df.loc[df.name == name].name[0],
             "department": df.loc[df.name == name].department[0],
             "birthday": df.loc[df.name == name].birthday[0],
             }, sort_keys=True, indent=4),
        headers={"Content-Type": "application/json"})


def update_record(ctx, data):
    try:
        name, department, birthday = read_data(data)
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


def delete_record(ctx):
    df = pd.read_csv(csv_api_url)
    df.drop(0, axis=0, inplace=True)
    object_storage.put_object(namespace, bucket_name, 'db.csv', df.to_csv())
    return response.Response(
            ctx, response_data=json.dumps(
                {
                    "Message": "deleted the first row"},
                sort_keys=True, indent=4),
            headers={"Content-Type": "application/json"}
        )


def read_data(data):
    body = json.loads(data.getvalue())
    name = str(body.get("name"))
    department = str(body.get("department"))
    birthday = str(body.get("birthday"))
    return name, department, birthday
