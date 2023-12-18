/**
 * Welcome to Cloudflare Workers! This is your first worker.
 *
 * - Run `npm run dev` in your terminal to start a development server
 * - Open a browser tab at http://localhost:8787/ to see your worker in action
 * - Run `npm run deploy` to publish your worker
 *
 * Learn more at https://developers.cloudflare.com/workers/
 */

import handleProxy from './proxy';
import handleRedirect from './redirect';
import apiRouter from './router';
import GoogleAuth, { GoogleKey } from 'cloudflare-workers-and-google-oauth'

async function handle_BQ_Request(request, env) {

	const scopes = ['https://www.googleapis.com/auth/bigquery']
	const googleAuth = JSON.parse(env.BIGQUERY_KEY)

	// Initialize the service
	const oauth = new GoogleAuth(googleAuth, scopes)
	const token = await oauth.getGoogleAuthToken()
	
	// Your SQL query
	const query = 'SELECT agg.table.* FROM (SELECT stop_id, ARRAY_AGG(STRUCT(table) ORDER BY insertion_time DESC)[SAFE_OFFSET(0)] agg FROM `eco-folder-402813.jeep_etas.test` table GROUP BY stop_id)';
    
	const response = await fetch(
		'https://bigquery.googleapis.com/bigquery/v2/projects/eco-folder-402813/queries', {
		method: 'POST',
		headers: {
			'Authorization': `Bearer ${token}`,
			'Content-Type': 'application/json'
		},
		body: JSON.stringify({
			query: query,
			useLegacySql: false
		})
	})

	// Parse and return the response
	// const result = response.json();
	// return new Response(JSON.stringify(result), {
	// 	headers: {'Content-Type': 'application/json'},
	// });

	return new Response(response.body);
}

// Export a default object containing event handlers
export default {
	// The fetch handler is invoked when this worker receives a HTTP(S) request
	// and should return a Response (optionally wrapped in a Promise)
	async fetch(request, env, ctx) {
		// You'll find it helpful to parse the request.url string into a URL object. Learn more at https://developer.mozilla.org/en-US/docs/Web/API/URL
		const url = new URL(request.url);

		// You can get pretty far with simple logic like if/switch-statements
		switch (url.pathname) {
			case '/redirect':
				return handleRedirect.fetch(request, env, ctx);

			case '/proxy':
				return handleProxy.fetch(request, env, ctx);
		}

		if (url.pathname.startsWith('/api/')) {
			// You can also use more robust routing
			return apiRouter.handle(request);
		}
		if (url.pathname.startsWith('/query')) {
			// You can also use more robust routing
			return handle_BQ_Request(request, env);
		}

		return new Response(
			`Try making requests to:
      <ul>
      <li><code><a href="/redirect?redirectUrl=https://example.com/">/redirect?redirectUrl=https://example.com/</a></code>,</li>
      <li><code><a href="/proxy?modify&proxyUrl=https://example.com/">/proxy?modify&proxyUrl=https://example.com/</a></code>, or</li>
      <li><code><a href="/api/todos">/api/todos</a></code></li>`,
			{ headers: { 'Content-Type': 'text/html' } }
		);
	},
};
