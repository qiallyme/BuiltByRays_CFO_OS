async function ask() {
    const question = document.getElementById("question").value;
    const res = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question })
    });
    const data = await res.json();
    document.getElementById("response").innerText = data.response;
}

