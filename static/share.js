const mastodon = document.querySelector(".mastodon-share");

function redirect(url) {
    content = `
        My developer portfolio got absolutely ROASTED:\n
        ${document.querySelector("#the-actual-thing").innerHTML}\n
        #devportfolioroast
    `;
    window.location.href = `https://${url}/share?text=${encodeURIComponent(content)}&url=${encodeURIComponent("https://profile-roast.thefossrant.com")}`;
}





mastodon.addEventListener("click", (e) => {
    if (localStorage.getItem("mastodon-instance")) {
        redirect(localStorage.getItem('mastodon-instance'));
    } else {
        e.preventDefault();
        let instance = window.prompt(
            'Please tell me your Mastodon instance'
        );
        localStorage.setItem('mastodon-instance', instance);

        redirect(localStorage.getItem('mastodon-instance'));
    }
});

twitter.addEventListener("click", (e) => {
    redirect("x.com");
});