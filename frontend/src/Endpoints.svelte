<script>
  import ConfirmModal from "./ConfirmModal.svelte";
  import { onMount } from "svelte";
  import { navigate, Link } from "svelte-routing";
  import NavBar from "./NavBar.svelte";
  import { slide } from "svelte/transition";

  let showModal = false;
  let jobToDelete = null;
  let isLoading = true;
  let isDeleting = false;
  let username = localStorage.getItem("username") || "";

  let jobs = [];

  $: {
    if (username === "") {
      navigate("/signin");
    }
  }

  async function getJobs(username) {
    isLoading = true;
    const response = await fetch(
      "http://flask-backend-alb-1415385398.us-east-1.elb.amazonaws.com/get_jobs",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ username }),
      }
    );

    const data = await response.json();
    console.log(data);

    jobs = data;
    isLoading = false;
  }

  onMount(async () => {
    await getJobs(username);
  });

  async function exportDocumentation(job, username) {
    const response = await fetch(
      "http://flask-backend-alb-1415385398.us-east-1.elb.amazonaws.com/export_docs",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          job_name: job.name,
          username: username,
          search_endpoint: `http://flask-backend-alb-1415385398.us-east-1.elb.amazonaws.com/search/${job.id}`,
          chat_endpoint: `http://flask-backend-alb-1415385398.us-east-1.elb.amazonaws.com/chat/${job.id}`,
        }),
      }
    );

    if (response.ok) {
      const data = await response.json();
      const markdownContent = data.md;

      const blob = new Blob([markdownContent], { type: "text/markdown" });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", `${job.name}_Documentation.md`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } else {
      console.error("Failed to export documentation");
    }
  }

  function toggle(job) {
    job.expanded = !job.expanded;
    jobs = jobs;
  }

  function confirmDelete(job) {
    showModal = true;
    jobToDelete = job;
  }

  async function deleteJob() {
    isDeleting = true;

    const response = await fetch(
      "http://flask-backend-alb-1415385398.us-east-1.elb.amazonaws.com/delete_job",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ name: jobToDelete.name, username: username }),
      }
    );

    if (response.ok) {
      jobs = jobs.filter((j) => j !== jobToDelete);
    } else {
      console.error("Failed to delete job");
    }

    isDeleting = false;
    showModal = false;
  }

  function cancelDelete() {
    showModal = false;
  }
</script>

<NavBar />
<div class="container mt-3">
  <h1 class="inference-header data-heading">
    <span class="title-animate title-word-1">All</span>
    <span class="title-animate title-word-2">Jobs</span>
  </h1>
  <hr />
  {#if isLoading}
    <h1
      style="text-align: center; font-size: 2em; font-weight: bold; color: black;"
    >
      Loading jobs...
    </h1>
  {:else}
    {#each jobs as job}
      <div class="job-card {job.expanded ? 'expanded' : ''}">
        <div class="job-info">
          <span class="job-title">{job.name}</span>
          <small class="job-date">{job.date}</small>
        </div>
        <div class="job-actions">
          {#if job.expanded}
            <span>Collapse to hide endpoints</span>
          {:else}
            <span>Expand to view endpoints</span>
          {/if}
          <button on:click={() => toggle(job)} class="btn toggle-btn">
            {job.expanded ? "Collapse" : "Expand"}
          </button>
        </div>
        {#if job.expanded}
          <div class="job-details" transition:slide={{ duration: 200 }}>
            <label for={`search-${job.name}`}>Search Endpoint:</label>
            <input
              type="text"
              id={`search-${job.name}`}
              value={"http://flask-backend-alb-1415385398.us-east-1.elb.amazonaws.com/search/" +
                job.id}
              class="form-control"
              readonly
            />

            <label for={`chat-${job.id}`}>Chat Endpoint:</label>
            <input
              type="text"
              id={`chat-${job.name}`}
              value={"http://flask-backend-alb-1415385398.us-east-1.elb.amazonaws.com/chat/" +
                job.id}
              class="form-control"
              readonly
            />

            <div>
              <button class="btn delete-btn" on:click={() => confirmDelete(job)}
                >Delete Job</button
              >
              <button
                class="btn export-btn"
                on:click={() => exportDocumentation(job, username)}
                >Export Documentation</button
              >
            </div>
          </div>
        {/if}
      </div>
    {/each}
    {#if showModal}
      <ConfirmModal
        message={isDeleting
          ? "Deleting..."
          : "Are you sure you want to delete this job?"}
        onConfirm={deleteJob}
        onCancel={cancelDelete}
      />
    {/if}
  {/if}
</div>

<style>
  h1 {
    font-size: 2em;
    font-weight: bold;
    margin-bottom: 20px;
  }

  .job-card {
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    padding: 10px;
    margin: 0px;
    border: 1px solid #ccc;
    background-color: #f9f9f9;
    border-radius: 10px;
  }

  .job-info,
  .job-actions {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  .job-title {
    font-size: 20px;
    font-weight: bold;
  }

  .job-date {
    font-size: 12px;
    color: #666;
    margin-top: 5px;
  }

  .job-actions span {
    font-size: 12px;
  }

  .expanded .job-details {
    display: block;
  }

  .form-control {
    padding: 5px;
    margin: 5px 0;
    width: 100%;
  }

  .btn {
    padding: 5px 10px;
    /* margin-left: 10px; */
    cursor: pointer;
  }

  .btn.toggle-btn {
    background-color: #210748;
    border: 1px solid #210748;
    color: white;
    text-align: center;
    text-decoration: none;
    display: inline-block;
    font-size: 16px;
    margin: 4px 2px;
    transition-duration: 0.1s;
    cursor: pointer;
    padding: 10px 24px;
  }

  .btn.toggle-btn:hover {
    background-color: white;
    color: black;
  }

  .delete-btn {
    background-color: #ff0000;
    border: 1px solid #ff0000;
    color: white;
    margin-top: 5px;
  }

  .export-btn {
    background-color: #4eb88e;
    border: 1px solid #4eb88e;
    color: white;
    margin-top: 5px;
  }
</style>
