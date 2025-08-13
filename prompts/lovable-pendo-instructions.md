Next we need to add Pendo tracking to this application.

Step 1: Insert the Pendo Agent Script in index.html

Open public/index.html and insert the following snippet just before the closing </body> tag:

<script>
(function(apiKey){
    (function(p,e,n,d,o){var v,w,x,y,z;o=p[d]=p[d]||{};o._q=o._q||[];
    v=['initialize','identify','updateOptions','pageLoad','track'];for(w=0,x=v.length;w<x;++w)(function(m){
        o[m]=o[m]||function(){o._q[m===v[0]?'unshift':'push']([m].concat([].slice.call(arguments,0)));};})(v[w]);
        y=e.createElement(n);y.async=!0;y.src='https://cdn.pendo.io/agent/static/'+apiKey+'/pendo.js';
        z=e.getElementsByTagName(n)[0];z.parentNode.insertBefore(y,z);})(window,document,'script','pendo');

    // Do NOT call initialize here — it should happen in App.tsx
})('<your-pendo-api-key-here>');
</script>

🔁 Replace '<your-pendo-api-key-here>' with the actual API key.
For demo environments, keep this as a placeholder unless the user provides a real key.

⸻
Step 2: Call pendo.initialize() in App.tsx

In src/App.tsx, initialize Pendo when the app knows the logged-in user. Example:

useEffect(() => {
  if (window.pendo) {
    window.pendo.initialize({
      visitor: {
        id: '<visitor-id>' // Replace dynamically with logged-in user ID
        // email: '<email>', // optional
        // full_name: '<full name>', // optional
      },
      account: {
        id: '<account-id>' // Replace dynamically with org/account ID
        // name: '<account name>', // optional
      }
    });
  }
}, []);

🔒 Use placeholders (<visitor-id>, <account-id>) unless real values are known.
These must be strings, numbers, or booleans — no objects or null values.

⸻

Step 3: Tag Core UI Elements with data-pendo-id

If the app’s UI does not already use data-pendo-id attributes (or a similar unique ID) that we can use for pendo tracking, add them. Every core user element like button or input form need to have a distinct tag.
<button data-pendo-id="start-trial-button">Start Trial</button>

Use descriptive, unique IDs like:
	•	login-submit
	•	dashboard-link
	•	feature-X-tab

