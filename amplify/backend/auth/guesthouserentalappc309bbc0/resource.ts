import { defineAuth } from '@aws-amplify/backend';


/**
 * Define and configure your auth resource
 * @see https://docs.amplify.aws/gen2/build-a-backend/auth
 */
export const auth = defineAuth({
  loginWith: {
    email: true,
    phone: true
  },
  userAttributes: {
    preferredUsername: {
      mutable: true,
      required: false
    },
      // specify a "birthdate" attribute
      birthdate: {
        mutable: true,
        required: false,
      }
  
  }
});