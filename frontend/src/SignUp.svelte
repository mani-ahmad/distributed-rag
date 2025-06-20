<script>
	import { navigate, Link } from 'svelte-routing';
	import NavBar from './NavBar.svelte';
	import { CognitoUserPool } from 'amazon-cognito-identity-js';
	import { COGNITO_CONFIG } from './lib/config.js';  

	const poolData = {
		UserPoolId: COGNITO_CONFIG.USER_POOL_ID,
		ClientId: COGNITO_CONFIG.CLIENT_ID
	};
	const userPool = new CognitoUserPool(poolData);

	let username = '';
	let password = '';
	let role = '';  

	const handleSubmit = async (event) => {
		event.preventDefault();

		userPool.signUp(username, password, [], null, (err, result) => {
			if (err) {
				alert(`Sign up failed: ${err.message}`);
				console.error("Sign up error:", err);
				return;
			}
			console.log("Sign up successful:", result);
			alert("Sign up successful! Please confirm your email before logging in.");
			navigate("/confirm", { state: { username } });  
		});
	};
</script>



<style>
	.white-hover:hover {
		color: black;
		background-color: white;
	}
	
</style>
<div class="patterns">
	<svg width="100%" height="100%">  
	<text x="50%" y="60%"  text-anchor="middle"  >
	DRAG
   </text>
   </svg>
  </div>
<NavBar />

<div class="login-box">
<h2>Create Account</h2>

<form id="sign-up-form" on:submit={handleSubmit}> <div class="user-box">
	<input type="text" name="username" id="username" required="" maxlength="50" bind:value={username}><label for="username">Username</label>
	<span class="error-message"></span> </div>
	<div class="user-box">
	<input type="password" name="password" id="password" required="" minlength="8" bind:value={password}><label for="password">Password</label>
	<span class="error-message"></span> </div>
	<button type="submit" >Sign Up</button>
</form>
</div>
<!-- <script src="validation.js"></script> -->