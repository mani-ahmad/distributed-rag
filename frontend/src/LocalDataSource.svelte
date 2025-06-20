<script>
  import { onMount } from "svelte";
  import { navigate, Link } from "svelte-routing";
  import NavBar from "./NavBar.svelte";
  import JSZip from "jszip";

  let file;
  let name = "";
  let uploadButtonDisabled = true;
  let fileName = "";
  let fileInput;
  let username = localStorage.getItem("username") || "";

  $: {
    if (file) {
      analyzeFile();
    }

    if (username === "") {
      navigate("/signin");
    }
  }

  function onDragOver(event) {
    event.preventDefault();
  }

  function onDrop(event) {
    event.preventDefault();
    if (
      event.dataTransfer.items &&
      event.dataTransfer.items[0].kind === "file"
    ) {
      file = event.dataTransfer.items[0].getAsFile();
      fileName = file.name;
      uploadButtonDisabled = !file || name === "";
    }
  }

  function onFileChange(event) {
    file = fileInput.files[0];
    fileName = file.name;
    uploadButtonDisabled = !file || name === "";
  }

  function onNameChange(event) {
    name = event.target.value;
    uploadButtonDisabled = !file || name === "";
  }

  function onUploadContainerClick() {
    document.getElementById("fileInput").click();
  }

  function analyzeFile() {
    if (file) {
      const reader = new FileReader();
      reader.onload = function (event) {
        const zip = new JSZip();
        zip.loadAsync(event.target.result).then(function (zip) {
          var files = Object.values(zip.files);
          const tableBody = document.querySelector(".table tbody");
          tableBody.innerHTML = "";

          files = files.filter((file) => file._data.uncompressedSize > 0);

          files.forEach(function (file, index) {
            const row = document.createElement("tr");
            const numberCell = document.createElement("td");
            const nameCell = document.createElement("td");
            const sizeCell = document.createElement("td");
            const dateCell = document.createElement("td");

            numberCell.textContent = index + 1;
            nameCell.textContent = file.name.split("/").pop();
            sizeCell.textContent = file._data.uncompressedSize + " bytes";
            dateCell.textContent = new Date(file.date).toLocaleString();
            dateCell.style.textAlign = "right";

            row.appendChild(numberCell);
            row.appendChild(nameCell);
            row.appendChild(sizeCell);
            row.appendChild(dateCell);

            tableBody.appendChild(row);
          });
        });
      };
      reader.readAsArrayBuffer(file);
    }
  }

  let isLoading = false;
  let modal = { isOpen: false, message: "", isSuccess: true };

  async function upload() {
    isLoading = true;
    const formData = new FormData();
    formData.append("file", file);
    formData.append("name", name);
    formData.append("username", username);

    try {
      const response = await fetch(
        "http://flask-backend-alb-1415385398.us-east-1.elb.amazonaws.com/upload_local_data",
        {
          method: "POST",
          body: formData,
        }
      );

      if (response.ok) {
        modal = {
          isOpen: true,
          message: "File uploaded successfully",
          isSuccess: true,
        };
      } else {
        modal = {
          isOpen: true,
          message: "File upload failed",
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
</script>

<NavBar />
<div class="container mt-3">
  <h1 class="data-heading">
    <span class="title-animate">Upload</span>
    <span class="title-animate">Local</span>
    <span class="title-animate">Data</span>
    <span class="title-animate">Source</span>
  </h1>
  <hr />

  <div class="name-field-container">
    <label for="dataSourceName" class="form-label">Data Source Name:</label>
    <input
      type="text"
      class="form-control"
      id="dataSourceName"
      placeholder="Enter name for the data source"
      bind:value={name}
      on:input={onNameChange}
    />
  </div>

  <!-- svelte-ignore a11y-click-events-have-key-events -->
  <div
    class="upload-container"
    on:dragover={onDragOver}
    on:drop={onDrop}
    on:click={onUploadContainerClick}
  >
    {#if isLoading}
      <div class="spinner-border text-dark" role="status">
        <span class="sr-only"></span>
      </div>
    {/if}
    <p style="color: grey;">
      Drag your zip file here or click to select a file
    </p>
    <label for="fileInput" class={fileName ? "visible" : "invisible"}
      >{fileName}</label
    >
    <input
      type="file"
      id="fileInput"
      accept=".zip"
      hidden
      bind:this={fileInput}
      on:change={onFileChange}
    />
    <!-- Modify this line -->
  </div>

  <button
    class="btn blackbtn-hover btn-outline-dark mt-2 w-100"
    disabled={uploadButtonDisabled}
    on:click={upload}>Upload Data Source</button
  >

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

  <div class="table-container">
    <table class="table">
      <thead>
        <tr>
          <th>#</th>
          <th>Document Name</th>
          <th>Size</th>
          <th>Date Modified</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td colspan="4" class="text-center">No documents yet</td>
        </tr>
      </tbody>
    </table>
  </div>
</div>

<style>
  .upload-container {
    padding: 20px;
    border: 2px dashed #ccc;
    border-radius: 5px;
    text-align: center;
    margin-bottom: 20px;
    cursor: pointer;
  }

  .table-container,
  .name-field-container {
    margin-top: 20px;
    margin-bottom: 20px;
  }

  .table {
    border-radius: 5px;
  }

  .blackbtn-hover {
    color: white;
    background-color: black;
    border: 1px solid black;
  }
  .blackbtn-hover:hover {
    color: black;
    background-color: white;
    border: 1px solid black;
  }

  .invisible {
    display: none;
  }
  .visible {
    display: block;
  }

  th {
    text-align: left;
  }

  th:last-child,
  td:last-child {
    text-align: right;
  }

  .form-label {
    font-weight: bold;
  }
</style>
