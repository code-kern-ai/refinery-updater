# function name tamplate: <service_name>_<version_with_underscore>
# example: update logic for service AUTHORIZER for version 1.2.2 would be def authorizer_1_2_2()->bool:
# should always return True if update logic was successful
# private functions can be used as helper functions, since they do not start with the service name
