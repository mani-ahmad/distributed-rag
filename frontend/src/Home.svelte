<script>
    import { navigate, Link } from 'svelte-routing';
    import NavBar from './NavBar.svelte';
  </script>
  
  <style>
  .main-body {
        margin-top: -20px;
    }

    .section {
        padding: 50px 0;
        background-color: #bcbdbc;
        color: #333;
        text-align: center;
        font-size: 1.25rem;
        font-family: 'Lato', sans-serif;
    }

    .section:nth-child(odd) {
        background-color: #222222;
        color: #f0f0f0;
    }

    .section h2 {
        text-align: center;
        color: #333;
        font-weight: 700;
    }

    .section p {
        padding-left: 10em;
        padding-right: 10em;
    }

    .section:nth-child(odd) h2 {
        color: #f0f0f0;
    }

    .btn-cta {
        display: inline-block;
        padding: 10px 20px;
        color: #3c3c3c;
        background-color: #fff;
        border-radius: 5px;
        text-decoration: none;
        transition: background-color 0.3s ease;
        border: none;
        font-size: 1.25rem;
        cursor: pointer;
        margin-right: 10px;
    }

    .btn-cta:hover {
        background-color: #dad1d1;
        color: black
    }

    .lato-light {
        font-family: "Lato", sans-serif;
        font-weight: 300;
        font-style: normal;
    }

    .lato-regular {
        font-family: "Lato", sans-serif;
        font-weight: 400;
        font-style: normal;
    }

    .lato-bold {
    font-family: "Lato", sans-serif;
    font-weight: 700;
    font-style: normal;
    }
  </style>
  
  <NavBar />
  
  <div class="main-body">
    <section class="section">
        <h2 class="lato-bold">Welcome to DRAG</h2>
        <p class="lato-regular">
            DRAG, short for Distributed RAG, is a revolutionary RAG pipeline builder that offers both convenience and flexibility. With DRAG, you can easily build and manage your RAG pipelines in a distributed environment, ensuring optimal performance and scalability.
        </p>
    </section>

    <section class="section">
        <h2 class="lato-bold">What is RAG?</h2>
        <p class="lato-regular">
            RAG, or Retrieval-Augmented Generation, is a powerful technique used in Natural Language Processing (NLP) that combines the strengths of both retrieval-based and generative systems. With RAG, you can generate responses that are not only contextually relevant but also factually accurate, making it ideal for tasks such as question answering, dialogue systems, and more.
        </p>
    </section>

    <section class="section">
        <h2 class="lato-bold">Why Choose DRAG?</h2>
        <p class="lato-regular">
            DRAG is designed with the enterprise user in mind. It offers a user-friendly interface that makes it easy to build, manage, and optimize your RAG pipelines. Plus, with its distributed architecture, DRAG ensures that your pipelines are highly scalable and performant, making it the perfect choice for both small and large-scale NLP projects.
        </p>
        <button class="btn-cta" on:click={() => navigate('/signup')}>Get Started</button>
        <a href="https://aarash-ab.gitbook.io/distributed-rag-user-documentation/" target="_blank" class="btn-cta">View Docs</a>
    </section>
</div>
  