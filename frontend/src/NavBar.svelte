<script>
	import { navigate, Link } from 'svelte-routing';

  let username = localStorage.getItem('username') || '';

  function handleLogout() {
        username = '';
        localStorage.setItem('username', '');
        navigate('/signin');
  }
</script>

<style>
  a {
      text-decoration: none;
  }
  .navbar{
    background-color: rgb(0, 0, 0);
  }
  .item{
    color:black
  }
</style>

<nav class="navbar navbar-expand-sm "> <div class="container-fluid">
    <a class="navbar-brand text-white  px-3" href="#">DRAG</a>
    <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarSupportedContent" aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
      <span class="navbar-toggler-icon"></span>
    </button>
    <div class="collapse navbar-collapse" id="navbarSupportedContent">
        <div class="collapse navbar-collapse justify-content-center" id="navbarSupportedContent">
            <ul class="navbar-nav mb-2 mb-lg-0">
              <li class="nav-item px-3">
                <Link to="/" style="text-decoration: none; color: inherit;"><a class="nav-link text-white highlight-on-hover" aria-current="page" href="#">Home</a></Link>
              </li>
              <ul class="navbar-nav ms-auto">
                <li class="nav-item px-3 dropdown">  <a class="nav-link text-white highlight-on-hover dropdown-toggle" data-bs-toggle="dropdown" href="#" aria-expanded="false">Add Data Source</a> 
                    <ul class="dropdown-menu">  
						<li>
							<Link to="/localdatasource" style="text-decoration: none; color: white;"><a class=" item dropdown-item">Local</a></Link>
						</li>
					</ul>
                </li>
                </ul>
              <li class="item nav-item px-3">
                <Link to="/configuration" style="text-decoration: none; color: black;"><a class="nav-link text-white highlight-on-hover" href="#">Set Configuration</a></Link>
              </li>
              <li class="item nav-item px-3">
                <Link to="/inference" style="text-decoration: none; color: inherit;"><a class="nav-link text-white highlight-on-hover" href="#">Run Inference</a></Link>
              </li>
              <li class=" item nav-item px-3">
                <Link to="endpoints" style="text-decoration: none; color: inherit;"><a class="nav-link text-white highlight-on-hover" href="#">Vector Endpoints</a></Link>
              </li>
            </ul>
          </div>          
          <ul class="navbar-nav ms-auto">
            {#if username == ''}
                <li class="nav-item">
                    <Link to='/signup' style="text-decoration: none; color: inherit;"><a class="btn btn-outline-light white-hover">Sign up</a></Link>
                </li>
                <li class="nav-item ms-3">
                    <Link to="/signin" style="text-decoration: none; color: inherit;"><a class="btn btn-outline-light white-hover">Log in</a></Link>
                </li>
            {:else}
                <li class="nav-item">
                    <button class="btn btn-outline-light white-hover" on:click={handleLogout}>Logout</button>
                </li>
            {/if}
          </ul>
          
    </div>
  </div>
</nav>