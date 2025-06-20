<script>
  import { navigate } from "svelte-routing";
  import NavBar from "./NavBar.svelte";
  import {
    CognitoUserPool,
    CognitoUser,
    AuthenticationDetails,
  } from "amazon-cognito-identity-js";
  import { COGNITO_CONFIG } from "./lib/config.js";

  // Setup Cognito User Pool
  const poolData = {
    UserPoolId: COGNITO_CONFIG.USER_POOL_ID,
    ClientId: COGNITO_CONFIG.CLIENT_ID,
  };
  const userPool = new CognitoUserPool(poolData);

  let username = "";
  let password = "";

  function sanitizeForAwsName(input) {
    return input
      .replace(/[^a-zA-Z0-9-]/g, "-")
      .replace(/-+/g, "-")
      .replace(/^-|-$/g, "")
      .substring(0, 63);
  }

  const handleSubmit = (event) => {
    event.preventDefault();

    const userData = {
      Username: username,
      Pool: userPool,
    };
    const cognitoUser = new CognitoUser(userData);

    const authDetails = new AuthenticationDetails({
      Username: username,
      Password: password,
    });

    cognitoUser.authenticateUser(authDetails, {
      onSuccess: async (result) => {
        console.log("Sign in successful:", result);
        alert("Sign in successful!");
        // localStorage.setItem('username', username);
        const sanitizedUsername = sanitizeForAwsName(username);
        localStorage.setItem("username", sanitizedUsername);

        const backendUrl =
          "http://flask-backend-alb-1415385398.us-east-1.elb.amazonaws.com";
        try {
          const response = await fetch(`${backendUrl}/add_user`, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({ username: sanitizedUsername }),
          });

          if (!response.ok) {
            throw new Error(`Backend error: ${response.status}`);
          }

          const data = await response.json();
          console.log("User added to backend:", data);
        } catch (err) {
          console.error("Failed to notify backend:", err);
        }

        navigate("/localdatasource");
      },
      onFailure: (err) => {
        if (err.code === "UserNotConfirmedException") {
          alert("Please confirm your email before logging in.");
          navigate("/confirm", { state: { username } });
        } else {
          alert(`Sign in failed: ${err.message}`);
          console.error("Sign in error:", err);
        }
      },
    });
  };
</script>

<div class="patterns">
  <svg width="100%" height="100%">
    <text x="50%" y="60%" text-anchor="middle"> DRAG </text>
  </svg>
</div>
<NavBar />

<div class="login-box">
  <h2>Welcome Back</h2>
  <form id="login-form" on:submit={handleSubmit}>
    <div class="user-box">
      <input
        type="text"
        name="username"
        required=""
        maxlength="50"
        bind:value={username}
      /> <label class="mb-2">Username</label>
      <span class="error-message"></span>
    </div>
    <div class="user-box">
      <input
        type="password"
        name="password"
        required=""
        minlength="8"
        bind:value={password}
      /> <label class="mb-2 pb-2">Password</label>
      <span class="error-message"></span>
    </div>
    <button class="login-btn" type="submit"> Log In </button>
  </form>
</div>

<style>
  .white-hover:hover {
    color: rgb(255, 255, 255);
    background-color: rgb(0, 0, 0);
  }

  .user-box label {
    margin-bottom: 20px;
  }
  .login-btn {
    border-radius: 8px;
    width: 80px;
    background-color: rgb(255, 255, 255);
    color: rgb(0, 0, 0);
  }
  .login-btn:hover {
    background: #3c3c3c;
    color: #fff;
    border-radius: 8px;
  }
</style>
