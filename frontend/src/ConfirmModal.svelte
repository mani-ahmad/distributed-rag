<script>
    export let message;
    export let onConfirm;
    export let onCancel;

    function handleConfirm() {
        onConfirm();
    }

    function handleCancel() {
        onCancel();
    }
</script>

<div class="modal">
    <div class="modal-content">
        <h5>{message}</h5>
        <button on:click={handleConfirm} class="btn confirm-btn">Confirm</button>
        <button on:click={handleCancel} class="btn cancel-btn">Cancel</button>
    </div>
</div>

<style>
    .modal {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0, 0, 0, 0.5);
        display: flex;
        justify-content: center;
        align-items: center;
    }

    .modal-content {
        background-color: #fff;
        padding: 20px;
        border-radius: 5px;
        width: 300px;
        text-align: center;
    }

    .btn {
        margin: 10px;
        padding: 10px 20px;
        border: none;
        color: white;
        cursor: pointer;
    }

    .confirm-btn {
        background-color: #4CAF50;
    }

    .cancel-btn {
        background-color: #f44336;
    }

    .confirm-btn:hover {
        background-color: #4CAF50;
    }

    .cancel-btn:hover {
        background-color: #f44336;
    }
</style>
