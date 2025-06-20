<script>
    import { Router, Route, Link , navigate} from 'svelte-routing';
    import SignUp from './SignUp.svelte';
	import SignIn from './SignIn.svelte';
	import LocalDataSource from './LocalDataSource.svelte';
    import Configuration from './Configuration.svelte';
	import Inference from './Inference.svelte';
	import Endpoints from './Endpoints.svelte';
	import Home from './Home.svelte';
	import ConfirmSignup from './ConfirmSignup.svelte'; 
</script>

<Router>  
    <Route path="/" let:params component={Home} />
    <Route path="signin" let:params component={SignIn} />
	<Route path="signup" let:params component={SignUp} />
	<Route path="confirm" let:params component={ConfirmSignup} />
	<Route path="localdatasource" component={LocalDataSource} />
	<Route path="configuration" component={Configuration} />
	<Route path="inference" component={Inference} />
	<Route path="endpoints" component={Endpoints} />
</Router>