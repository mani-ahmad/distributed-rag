import App from './App.svelte';
import { Router, Route, Link } from 'svelte-routing';
import { Buffer } from 'buffer';

window.Buffer = Buffer;

const app = new App({
	target: document.body,
});

export default app;