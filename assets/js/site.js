const buttons = [...document.querySelectorAll("[data-filter]")];
const cards = [...document.querySelectorAll("[data-tags]")];
const count = document.querySelector("[data-count]");

if (buttons.length && cards.length) {
  const applyFilter = (filter) => {
    let visible = 0;

    cards.forEach((card) => {
      const tags = (card.dataset.tags || "").split(" ").filter(Boolean);
      const show = filter === "all" || tags.includes(filter);
      card.classList.toggle("hidden", !show);
      if (show) {
        visible += 1;
      }
    });

    buttons.forEach((button) => {
      button.classList.toggle("is-active", button.dataset.filter === filter);
    });

    if (count) {
      count.textContent = `${visible} entry${visible === 1 ? "" : "ies"} showing`;
    }
  };

  buttons.forEach((button) => {
    button.addEventListener("click", () => applyFilter(button.dataset.filter));
  });

  applyFilter("all");
}
