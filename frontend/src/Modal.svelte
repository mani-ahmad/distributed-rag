<script>
    export let mode;

    function handleConfirm() {
        mode = '';
    }
</script>

{#if mode !== ''}
    <div class="modal">
        <div class="modal-content">
            {#if mode === 'loading'}
                <h5>Loading...</h5>
            {:else if mode === 'success'}
                <h5>Success!</h5>
                <button on:click={handleConfirm} class="btn confirm-btn">OK</button>
            {:else if mode === 'failure'}
                <h5>Failure!</h5>
                <button on:click={handleConfirm} class="btn cancel-btn">OK</button>
            {/if}
        </div>
    </div>
{/if}

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
        z-index: 9999;
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