Link to github:
https://github.com/JaKourdi/oracle-cloud-func-2 


Link to app2:
https://m7l2i2ximv4pqfi3xlea5yb53u.apigateway.il-jerusalem-1.oci.customer-oci.com/app2/



APIs:
 - GET CSV:
 https://m7l2i2ximv4pqfi3xlea5yb53u.apigateway.il-jerusalem-1.oci.customer-oci.com/app2/getcsv
 
 - Add record to csv:
 
 curl --location --request POST 'https://m7l2i2ximv4pqfi3xlea5yb53u.apigateway.il-jerusalem-1.oci.customer-oci.com/app2/' \
--header 'Content-Type: application/json' \
--data-raw '{
  "name":"yaakov",
  "department": "POP",
  "birthday month" : "22"
}'


- Update an existing record in CSV:


curl --location --request DELETE 'https://m7l2i2ximv4pqfi3xlea5yb53u.apigateway.il-jerusalem-1.oci.customer-oci.com/app2/'
