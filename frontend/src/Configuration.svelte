<script>
  import { navigate, Link } from "svelte-routing";
  import NavBar from "./NavBar.svelte";
  import { onMount } from "svelte";

  let configName = "";

  let regexPattern = "";
  let regexReplacement = "";

  let batchSize = 256;
  let gpu = "a10g";
  let embeddingModel = "";
  let numWorkers = 2;

  let username = localStorage.getItem("username") || "";

  let isLoading = false;
  let modal = { isOpen: false, message: "", isSuccess: true };

  let isFormValid = () =>
    configName &&
    configName !== "" &&
    batchSize &&
    batchSize > 0 &&
    numWorkers &&
    numWorkers > 0 &&
    gpu &&
    embeddingModel &&
    embeddingModel !== "" &&
    username &&
    username !== "";

  let isFormInvalid = false;

  $: {
    if (username === "") {
      navigate("/signin");
    }
  }

  async function saveConfig() {
    if (!isFormValid()) {
      isFormInvalid = true;
      return;
    }

    isFormInvalid = false;
    isLoading = true;
    const config = {
      batchSize,
      gpu,
      embeddingModel,
      regexPattern,
      regexReplacement,
      configName,
      username,
      num_workers: numWorkers,
    };

    try {
      console.log(JSON.stringify(config));
      const response = await fetch(
        "http://flask-backend-alb-1415385398.us-east-1.elb.amazonaws.com/save_config",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(config),
        }
      );

      if (response.ok) {
        modal = {
          isOpen: true,
          message: "Config saved successfully",
          isSuccess: true,
        };
      } else {
        modal = {
          isOpen: true,
          message: "Failed to save config",
          isSuccess: false,
        };
      }
    } catch (error) {
      modal = { isOpen: true, message: "An error occurred", isSuccess: false };
    } finally {
      isLoading = false;
    }
  }

  function closeModal() {
    modal.isOpen = false;
  }

  let embeddingModels = [];

  onMount(async () => {
    try {
      const response = await fetch(
        "http://flask-backend-alb-1415385398.us-east-1.elb.amazonaws.com/get_models_list",
        {
          method: "GET",
        }
      );
      if (response.ok) {
        const data = await response.json();
        embeddingModels = Object.keys(data["models"]);
        embeddingModel = embeddingModels[0];
        console.log("Embedding models:", data);
      } else {
        console.error("Failed to fetch embedding models");
      }
    } catch (error) {
      console.error("An error occurred when fetching embedding models:", error);
    }
  });
</script>

<NavBar />
<div class="container mt-3 mb-10">
  <h1 class="config-header data-heading">
    <span class="title-animate title-word-1">Configuration</span>
    <span class="title-animate title-word-2">Setup</span>
  </h1>
  <hr />

  <form class="config-container was-validated">
    <div class="mb-3">
      <label for="numWorkers" class="form-label">Number of Workers:</label>
      <input
        type="number"
        class="form-control"
        id="numWorkers"
        min="1"
        bind:value={numWorkers}
        required
      />
    </div>
    <div class="mb-3">
      <label for="numWorkers" class="form-label">Batch Size:</label>
      <input
        type="number"
        class="form-control"
        id="numWorkers"
        min="1"
        bind:value={batchSize}
      />
    </div>

    <div class="mb-3">
      <label for="gpuSelect" class="form-label">GPU:</label>
      <select class="form-select" id="gpuSelect" bind:value={gpu}>
        <option value="A10G">Nvidia A10G</option>
        <option value="T4">Nvidia T4</option>
        <option value="A100">Nvidia A100</option>
        <option value="H100">Nvidia H100</option>
      </select>
    </div>

    <div class="mb-3">
      <label for="embeddingModelSelect" class="form-label"
        >Embedding Model:</label
      >
      <select
        class="form-select"
        id="embeddingModelSelect"
        bind:value={embeddingModel}
      >
        {#each embeddingModels as model (model)}
          <option value={model}>{model}</option>
        {/each}
      </select>
    </div>

    <div class="mb-3">
      <label for="regexPattern" class="form-label">Regex Pattern:</label>
      <input
        type="text"
        class="form-control"
        id="regexPattern"
        placeholder="Enter regex pattern"
        bind:value={regexPattern}
      />

      <label for="regexReplacement" class="form-label"
        >Replacement String:</label
      >
      <input
        type="text"
        class="form-control"
        id="regexReplacement"
        placeholder="Enter regex replacement string"
        bind:value={regexReplacement}
      />
    </div>

    <div class="mb-3">
      <label for="configName" class="form-label">Config Name:</label>
      <input
        type="text"
        class="form-control"
        id="configName"
        required
        placeholder="Name to save the config by"
        bind:value={configName}
      />
      <button
        type="submit"
        class="w-100 btn white-hover btn-outline-light"
        on:click|preventDefault={saveConfig}
        disabled={configName === ""}
        title={isFormInvalid
          ? "All fields are required except regex fields"
          : ""}
      >
        Save Config
      </button>
    </div>

    {#if modal.isOpen}
      <div
        class="modal show"
        tabindex="-1"
        role="dialog"
        style="display: block; background-color: rgba(0, 0, 0, 0.5);"
      >
        <div class="modal-dialog">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title">
                {modal.isSuccess ? "Success" : "Failure"}
              </h5>
              <button
                type="button"
                class="close"
                aria-label="Close"
                on:click={closeModal}
              >
                <span aria-hidden="true">&times;</span>
              </button>
            </div>
            <div class="modal-body">
              <p>{modal.message}</p>
            </div>
            <div class="modal-footer">
              <button
                type="button"
                class="btn btn-secondary"
                on:click={closeModal}>Close</button
              >
            </div>
          </div>
        </div>
      </div>
    {/if}
  </form>
</div>

<style>
  /* You can add or modify styles here to match the theme of your app */
  .config-container {
    margin-top: 20px;
  }

  .config-header {
    margin-bottom: 20px;
  }

  .form-label {
    margin-bottom: 5px;
    font-weight: 600;
  }

  .form-select,
  .form-control {
    margin-bottom: 20px;
    color: black;
  }

  .white-hover:hover {
    color: black;
    background-color: white;
    border: 1px solid black;
  }

  .white-hover {
    color: white;
    background-color: black;
    border: 1px solid black;
  }

  .white-hover:disabled {
    color: #333;
    background-color: #f0f0f0;
    border: 1px solid #ccc;
  }
</style>
