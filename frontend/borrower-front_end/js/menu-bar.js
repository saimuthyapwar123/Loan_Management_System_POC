const profileToggle = document.getElementById("profileToggle");
const profilePanel = document.getElementById("profilePanel");

profileToggle.addEventListener("click", (e) => {
    e.stopPropagation();

    const isActive = profilePanel.classList.contains("active");

    if (isActive) {
        closeSidebar();
    } else {
        openSidebar();
    }
});

document.addEventListener("click", (e) => {
    if (!e.target.closest(".profile-panel") &&
        !e.target.closest("#profileToggle")) {
        closeSidebar();
    }
});

function openSidebar() {
    profilePanel.classList.add("active");
    document.body.classList.add("sidebar-active"); 
}

function closeSidebar() {
    profilePanel.classList.remove("active");
    document.body.classList.remove("sidebar-active"); 
}
