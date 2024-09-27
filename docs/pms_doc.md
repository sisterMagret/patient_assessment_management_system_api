**Overview**

FARMEAT is software solution meant not just to connect farmer's to consumers to carryout transactions on products smoothly, but also provides means for consumers or investors to also invest in farmers for their products or pre ordered products. The app also provides a logistic platform which can serve as a buffer between consumer and farmers during transactions.

**Authentication flow**

User authentication flow is being handled by a separated microservice that is being hosted separately on a domain name ``id.farmfeat.com`` , this microservice handle all the authentication and authorization that is being carried out on the system.



**USER CATEGORY PAYLOAD**:

    SELLER ONBOARDING 
    Payload:
        first_name
        last_name
        mobile
        password
        is_accept_terms_and_condition (True/False)
        

    BUYER ONBOARDING
    Payload:
        first_name
        last_name
        email
        phone
        password
        type -> this can either be individual or business
        business_name -> to be added to payload if ``type`` is business


