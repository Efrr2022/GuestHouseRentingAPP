// The file can be replaced during build by using the `fileReplacements` array.
// `ng build` replaces `environment.ts` with `environment.prod.ts`.
// The list of file replacements can be found in `angular.json`.

export const environment = {
    production:false,
       cognito: {
            region: "us-east-1",
            userPoolId:'us-east-1_JYVPbsTOO',
            userPoolWebClientId:'407mt8ve12lkmr5vl85hpaba0g',
           IdentityPoolId: 'us-east-1:49615bb0-9acb-49bf-97c3-7b741a04d643',

    }
};

/**
 * For easier debugging in development mode, you can import the following file
 * to ignore zone related error stack frames such as `zone.run`, `zoneDelegate.invokeTask`.
 * 
 * This import should be commented out in production mode because it will have a negative
 * on perfomance if an error is throw.
 */
// import 'zone.js/plugins/zone-error'; // Included with Angular CLI. 

