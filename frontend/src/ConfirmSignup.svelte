<script>
	import { navigate } from 'svelte-routing';
	import { useLocation } from 'svelte-routing';
	import { CognitoUserPool, CognitoUser } from 'amazon-cognito-identity-js';
	import { COGNITO_CONFIG } from './lib/config.js'; 

	// Setup CognitoUserPool directly here:
	const poolData = {
		UserPoolId: COGNITO_CONFIG.USER_POOL_ID,
		ClientId: COGNITO_CONFIG.CLIENT_ID
	};
	const userPool = new CognitoUserPool(poolData);

	// Get passed username from signup page
	const loc = useLocation();
	$: passedState = $loc.state;
	let username = passedState ? passedState.username : '';
	let code = '';

	const handleConfirm = (event) => {
		event.preventDefault();

		const userData = {
			Username: username,
			Pool: userPool
		};

		const cognitoUser = new CognitoUser(userData);

		cognitoUser.confirmRegistration(code, true, (err, result) => {
			if (err) {
				alert(`Confirmation failed: ${err.message}`);
				console.error('Confirmation error:', err);
				return;
			}
			alert('Account confirmed successfully! You can now log in.');
			navigate('/signin');
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
		<text x="50%" y="60%" text-anchor="middle">DRAG</text>
	</svg>
</div>

<div class="login-box">
	<h2>Confirm Your Account</h2>
	<form on:submit={handleConfirm}>
		<div class="user-box">
			<input type="text" placeholder="Username / Email" bind:value={username} required />
			<label>Username / Email</label>
		</div>
		<div class="user-box">
			<input type="text" placeholder="Verification Code" bind:value={code} required />
			<label>Verification Code</label>
		</div>
		<button type="submit">Confirm Account</button>
	</form>
</div>
