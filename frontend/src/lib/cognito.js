import {
    CognitoUserPool,
    CognitoUser,
    AuthenticationDetails
  } from 'amazon-cognito-identity-js';

  import { COGNITO_CONFIG } from './config.js';

  const poolData = {
    UserPoolId: COGNITO_CONFIG.USER_POOL_ID,
    ClientId: COGNITO_CONFIG.CLIENT_ID
  };

  export const userPool = new CognitoUserPool(poolData);
  export { CognitoUser, AuthenticationDetails };
  