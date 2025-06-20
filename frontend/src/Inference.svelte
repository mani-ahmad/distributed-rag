<script>
  import { navigate, Link } from "svelte-routing";
  import NavBar from "./NavBar.svelte";
  import { onMount } from "svelte";
  import Modal from "./Modal.svelte";

  let curDataSource = "";
  let dataSources = [];
  let configList = [];
  let selectedConfig = "";

  let runName = "";
  let requestStatus = "";

  let dataSourceType = "local";

  let dataSourceLoading = true;
  let configLoading = true;

  let isLoading;

  $: {
    isLoading = dataSourceLoading || configLoading;
  }

  let username = localStorage.getItem("username") || "";

  $: {
    if (dataSourceType === "local") {
      fetchLocalDataList(username);
    } else if (dataSourceType === "remote") {
      fetchRemoteDataList(username);
    }

    if (username === "") {
      navigate("/signin");
    }
  }

  async function fetchLocalDataList(username) {
    dataSourceLoading = true;
    const response = await fetch(
      "http://flask-backend-alb-1415385398.us-east-1.elb.amazonaws.com/get_local_data_list",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ username: username }),
      }
    );
    if (response.ok) {
      const data = await response.json();
      var datalist = data["files"];
      if (Array.isArray(datalist)) {
        dataSources = datalist;
        curDataSource = datalist[0]; // Set initial value to the first item in the list
      } else {
        console.error("Data sources is not an array:", datalist);
      }
    } else {
      console.error("Failed to fetch data sources");
    }

    dataSourceLoading = false;
  }

  async function getConfigList(username) {
    configLoading = true;
    const configResponse = await fetch(
      "http://flask-backend-alb-1415385398.us-east-1.elb.amazonaws.com/get_config_list",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ username }),
      }
    );
    if (configResponse.ok) {
      console.log(configResponse);
      const configData = await configResponse.json();
      if (Array.isArray(configData.configs)) {
        configList = configData.configs;
        selectedConfig = configList[0]; // Set initial value to the first item in the list
      } else {
        console.error("Config list is not an array:", configList);
      }
    } else {
      console.error("Failed to fetch config list");
    }
    configLoading = false;
  }

  onMount(async () => {
    try {
      username = localStorage.getItem("username") || "";
      if (dataSourceType === "local") {
        await fetchLocalDataList(username);
      } else if (dataSourceType === "remote") {
        await fetchRemoteDataList(username);
      }

      await getConfigList(username);

      isLoading = false;
    } catch (error) {
      console.error(
        "An error occurred when fetching data sources or config list:",
        error
      );
      isLoading = false;
    }
  });

  async function runJob() {
    try {
      requestStatus = "loading";
      const response = await fetch(
        "http://flask-backend-alb-1415385398.us-east-1.elb.amazonaws.com/run_job",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            config: selectedConfig,
            data: curDataSource,
            data_source_type: dataSourceType,
            job_name: runName,
            username: localStorage.getItem("username"),
          }),
        }
      );
      if (response.ok) {
        const data = await response.json();
        console.log("Job started successfully:", data);
        requestStatus = "success";
      } else {
        console.error("Failed to start job");
        requestStatus = "failure";
      }
    } catch (error) {
      console.error("An error occurred when starting the job:", error);
      requestStatus = "failure";
    }
  }
</script>

<NavBar />

{#if dataSourceLoading || configLoading}
  <div class="loading-symbol">
    <h3>Loading...</h3>
  </div>
{/if}

{#if !dataSourceLoading && !configLoading}
  <div class="container mt-3">
    <h1 class="inference-header data-heading">
      <span class="title-animate title-word-1">Run</span>
      <span class="title-animate title-word-2">Inference</span>
    </h1>
    <hr />

    <form
      class="inference-container was-validated"
      on:submit|preventDefault={runJob}
    >
      <div class="mb-3">
        <label for="runName" class="form-label">Name of Run:</label>
        <input
          type="text"
          class="form-control"
          id="runName"
          placeholder="Enter the name of the run"
          required
          bind:value={runName}
        />
      </div>

      <div class="mb-3">
        <label for="dataSourceSelect" class="form-label">Data Source:</label>
        <div class="radio-group">
          <div class="form-check">
            <input
              class="form-check-input"
              type="radio"
              name="dataSourceType"
              id="localDataSource"
              value="local"
              bind:group={dataSourceType}
            />
            <label class="form-check-label radio-choice" for="localDataSource">
              Local
            </label>
          </div>
          <div class="form-check">
            <input
              class="form-check-input"
              type="radio"
              name="dataSourceType"
              id="remoteDataSource"
              value="remote"
              bind:group={dataSourceType}
            />
            <label class="form-check-label radio-choice" for="remoteDataSource">
              Remote
            </label>
          </div>
        </div>
        <select
          class="form-select mt-2"
          id="dataSourceSelect"
          required
          bind:value={curDataSource}
        >
          {#each dataSources as dataSource (dataSource)}
            <option value={dataSource}>{dataSource}</option>
          {/each}
        </select>
      </div>

      <div class="mb-3">
        <label for="configSelect" class="form-label">Configuration:</label>
        <select
          class="form-select"
          id="configSelect"
          bind:value={selectedConfig}
        >
          {#each configList as config (config)}
            <option value={config}>{config}</option>
          {/each}
        </select>
      </div>

      <button
        type="submit"
        class="btn run-job-btn w-100 mt-3"
        disabled={runName === "" ||
          selectedConfig === "" ||
          curDataSource === ""}>Run Job</button
      >
    </form>
  </div>
  <Modal mode={requestStatus} />
{/if}

<style>
  .inference-container {
    margin-top: 20px;
  }

  .inference-header {
    margin-bottom: 20px;
  }

  .form-label {
    margin-bottom: 5px;
    font-weight: bold;
  }

  .form-select,
  .form-control {
    margin-bottom: 20px;
  }

  .run-job-btn {
    background-color: black;
    border: 1px solid black;
    color: white;
  }

  .run-job-btn:hover {
    background-color: white;
    color: black;
    border: 1px solid black;
  }

  .loading-symbol {
    text-align: center;
    margin-top: 20px;
    color: black;
  }

  .radio-choice {
    color: black;
  }

  .radio-group {
    display: flex;
    gap: 10px; /* Optional: Adds some space between the radio buttons */
  }

  .was-validated .form-check-input:invalid,
  .form-check-label {
    border-color: inherit;
    padding-right: inherit;
    background-image: inherit;
  }

  .was-validated .form-check-input:valid .form-check-label {
    border-color: inherit;
    padding-right: inherit;
    background-image: inherit;
  }

  .radio-choice {
    color: black;
  }
</style>
