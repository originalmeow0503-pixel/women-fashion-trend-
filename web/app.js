const STORAGE_KEY = "trendmuse_cart_v1";
const DEFAULT_PRODUCT_IMAGE = "assets/images/hero-banner.svg";
const state = {
  modelSummary: null,
  recommendations: [],
  sampleProducts: [],
  profilePredictions: [],
  trendsByAge: [],
  trendsByOccasion: [],
  productCatalog: [],
  productMap: new Map(),
  cart: loadCart(),
  loadIssues: [],
  runtimeMode: window.location.protocol === "file:" ? "file" : "server",
};

document.addEventListener("DOMContentLoaded", init);

async function init() {
  updateCartCount();
  await loadData();
  buildCatalog();
  updateCartCount();
  renderRuntimeNotice();

  const page = document.body.dataset.page;
  if (page === "home") {
    initHomePage();
  } else if (page === "cart") {
    initCartPage();
  } else if (page === "checkout") {
    initCheckoutPage();
  }

  bindGlobalEvents();
}

async function loadData() {
  state.loadIssues = [];

  // Opening the page with file:// prevents JSON fetch calls in many browsers.
  if (window.location.protocol === "file:") {
    state.runtimeMode = "file";
    state.modelSummary = {};
    state.recommendations = [];
    state.sampleProducts = [];
    state.profilePredictions = [];
    state.trendsByAge = [];
    state.trendsByOccasion = [];
    return;
  }

  const [modelSummary, recommendations, sampleProducts, profilePredictions, trendsByAge, trendsByOccasion] = await Promise.all([
    loadJson("data/model_summary.json", {}),
    loadJson("data/recommendations.json", []),
    loadJson("data/sample_products.json", []),
    loadJson("data/profile_predictions.json", []),
    loadJson("data/trends_by_age.json", []),
    loadJson("data/trends_by_occasion.json", []),
  ]);

  state.modelSummary = modelSummary;
  state.recommendations = recommendations.map(normalizeProduct);
  state.sampleProducts = sampleProducts.map(normalizeProduct);
  state.profilePredictions = profilePredictions.map((profile) => ({
    ...profile,
    products: (profile.products || []).map(normalizeProduct),
  }));
  state.trendsByAge = trendsByAge;
  state.trendsByOccasion = trendsByOccasion;
}

async function loadJson(path, fallback) {
  try {
    const response = await fetch(path);
    if (!response.ok) {
      throw new Error(`Failed to load ${path}`);
    }
    return await response.json();
  } catch (error) {
    state.loadIssues.push(path);
    return fallback;
  }
}

function normalizeProduct(product = {}) {
  return {
    ...product,
    image: normalizeImageUrl(product.image),
  };
}

function normalizeImageUrl(url) {
  if (!url) return DEFAULT_PRODUCT_IMAGE;
  return String(url).replace(/^http:\/\//i, "https://");
}

function renderRuntimeNotice() {
  const notice = document.getElementById("runtimeNotice");
  if (!notice) return;

  if (state.runtimeMode === "file") {
    notice.hidden = false;
    notice.innerHTML = "<strong>Open this page through a local server.</strong> This site loads exported JSON files, so opening <code>index.html</code> with <code>file://</code> will not show the same data as GitHub Pages. Use <code>http://localhost:8000</code> or VS Code Live Server.";
    return;
  }

  if (state.loadIssues.length) {
    notice.hidden = false;
    notice.innerHTML = `<strong>Some exported data files could not be loaded.</strong> Check that the server is rooted at the <code>web/</code> folder. Missing files: ${state.loadIssues.join(", ")}`;
    return;
  }

  notice.hidden = true;
}

function buildCatalog() {
  const map = new Map();

  state.recommendations.forEach((product) => {
    const key = buildProductKey(product);
    map.set(key, { ...product, key });
  });

  state.profilePredictions.forEach((profile) => {
    profile.products.forEach((product) => {
      const key = buildProductKey(product);
      if (!map.has(key)) {
        map.set(key, {
          ...product,
          key,
          age_group: profile.age_group,
          occasion: profile.occasion,
          recommendation_score: product.trend_score,
        });
      }
    });
  });

  state.productMap = map;
  state.productCatalog = Array.from(map.values());
}

function buildProductKey(product) {
  if (product.product_id) {
    return `pid-${product.product_id}`;
  }
  return `${product.name}__${product.brand || "brand"}__${product.price}`;
}

function loadCart() {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY) || "[]");
  } catch (error) {
    return [];
  }
}

function saveCart() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(state.cart));
}

function updateCartCount() {
  const total = state.cart.reduce((sum, item) => sum + item.quantity, 0);
  document.querySelectorAll("#cartCount").forEach((element) => {
    element.textContent = total;
  });
}

function addToCart(key) {
  const existing = state.cart.find((item) => item.key === key);
  if (existing) {
    existing.quantity += 1;
  } else {
    state.cart.push({ key, quantity: 1 });
  }
  saveCart();
  updateCartCount();
}

function changeQuantity(key, delta) {
  const item = state.cart.find((entry) => entry.key === key);
  if (!item) return;
  item.quantity += delta;
  if (item.quantity <= 0) {
    state.cart = state.cart.filter((entry) => entry.key !== key);
  }
  saveCart();
  updateCartCount();
}

function removeFromCart(key) {
  state.cart = state.cart.filter((entry) => entry.key !== key);
  saveCart();
  updateCartCount();
}

function getCartItemsDetailed() {
  return state.cart
    .map((item) => {
      const product = state.productMap.get(item.key);
      if (!product) return null;
      return {
        ...product,
        quantity: item.quantity,
        line_total: item.quantity * Number(product.price || 0),
      };
    })
    .filter(Boolean);
}

function formatCurrency(value) {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(Number(value || 0));
}

function initHomePage() {
  initHomeHeroSlider();
  renderMetrics();
  renderFeatured();
  renderProfileControls();
  renderAgeShowcase();
  renderOccasionShowcase();
  renderShop();
}

function initHomeHeroSlider() {
  const slides = Array.from(document.querySelectorAll(".home-hero-image"));
  const bars = Array.from(document.querySelectorAll(".pagination-bar"));
  if (slides.length < 2) return;

  let activeIndex = 0;

  const setActiveSlide = (index) => {
    activeIndex = index;
    slides.forEach((slide, slideIndex) => {
      slide.classList.toggle("active", slideIndex === index);
    });
    bars.forEach((bar, barIndex) => {
      bar.classList.toggle("active", barIndex === index);
    });
  };

  bars.forEach((bar, index) => {
    bar.addEventListener("click", () => setActiveSlide(index));
  });

  window.setInterval(() => {
    setActiveSlide((activeIndex + 1) % slides.length);
  }, 3600);
}

function renderMetrics() {
  if (!state.modelSummary) return;
  const dataset = document.getElementById("metricDataset");
  const accuracy = document.getElementById("metricAccuracy");
  const k = document.getElementById("metricK");
  const trend = document.getElementById("metricTrend");
  const heroCategory = document.getElementById("heroCategory");
  const heroImage = document.getElementById("heroImage");

  const hasAccuracy = typeof state.modelSummary.accuracy === "number";
  const topCategory = state.modelSummary.top_trending_category || "--";

  if (dataset) dataset.textContent = state.modelSummary.dataset_file || "Fashion Dataset.csv";
  if (accuracy) accuracy.textContent = hasAccuracy ? `${(state.modelSummary.accuracy * 100).toFixed(1)}%` : "--";
  if (k) k.textContent = state.modelSummary.best_params?.classifier__n_neighbors || "--";
  if (trend) trend.textContent = topCategory;
  if (heroCategory) heroCategory.textContent = topCategory === "--" ? "Awaiting Data" : topCategory;
  if (heroImage) {
    heroImage.src = state.sampleProducts[0]?.image || DEFAULT_PRODUCT_IMAGE;
    heroImage.alt = state.sampleProducts[0]?.name || "Featured fashion selection";
  }
}

function renderFeatured() {
  const grid = document.getElementById("featuredGrid");
  if (!grid) return;
  const featured = (state.sampleProducts.length ? state.sampleProducts : state.recommendations.slice(0, 8)).slice(0, 8);
  if (!featured.length) {
    grid.innerHTML = createEmptyStateCard("Start a local server to load the exported recommendation cards.");
    return;
  }
  grid.innerHTML = featured.map((product) => createProductCard(product)).join("");
}

function renderProfileControls() {
  const ageSelect = document.getElementById("ageSelect");
  const occasionSelect = document.getElementById("occasionSelect");
  const submitButton = document.querySelector('#profileForm button[type="submit"]');
  if (!ageSelect || !occasionSelect) return;

  const ageGroups = uniqueValues(state.profilePredictions.map((item) => item.age_group));
  const occasions = uniqueValues(state.profilePredictions.map((item) => item.occasion));

  if (!ageGroups.length || !occasions.length) {
    ageSelect.innerHTML = '<option value="">Local server required</option>';
    occasionSelect.innerHTML = '<option value="">JSON data required</option>';
    ageSelect.disabled = true;
    occasionSelect.disabled = true;
    if (submitButton) submitButton.disabled = true;
    setText("resultPill", "Awaiting Data");
    setText("resultCategory", "Exported results not loaded");
    setText("resultSummary", "Start a local server to load the exported profile predictions and recommendation cards.");
    setText("resultAge", "--");
    setText("resultOccasion", "--");
    setText("resultScore", "--");
    const container = document.getElementById("predictionProducts");
    if (container) {
      container.innerHTML = createEmptyStateCard("Profile-based product matches will appear here after the JSON files load.");
    }
    return;
  }

  ageSelect.innerHTML = ageGroups.map((value) => `<option value="${escapeHtml(value)}">${escapeHtml(value)}</option>`).join("");
  occasionSelect.innerHTML = occasions.map((value) => `<option value="${escapeHtml(value)}">${escapeHtml(value)}</option>`).join("");
  ageSelect.disabled = false;
  occasionSelect.disabled = false;
  if (submitButton) submitButton.disabled = false;

  renderProfileResult(ageGroups[0], occasions[0]);

  document.getElementById("profileForm")?.addEventListener("submit", (event) => {
    event.preventDefault();
    renderProfileResult(ageSelect.value, occasionSelect.value);
  });
}

function renderProfileResult(ageGroup, occasion) {
  const profile = state.profilePredictions.find((item) => item.age_group === ageGroup && item.occasion === occasion);
  if (!profile) return;

  const label = profile.trend_score >= 0.75 ? "High Trend" : profile.trend_score >= 0.55 ? "Rising Trend" : "Niche Trend";

  setText("resultPill", label);
  setText("resultCategory", profile.predicted_style);
  setText("resultSummary", profile.summary);
  setText("resultAge", profile.age_group);
  setText("resultOccasion", profile.occasion);
  setText("resultScore", profile.trend_score.toFixed(3));

  const container = document.getElementById("predictionProducts");
  if (container) {
    container.innerHTML = profile.products.map((product) => createMiniCard(product, profile.age_group, profile.occasion)).join("");
  }
}

function renderAgeShowcase() {
  const container = document.getElementById("ageRecommendationGrid");
  if (!container) return;

  if (!state.trendsByAge.length) {
    container.innerHTML = createEmptyStateCard("Age-group recommendations will appear here after the exported data loads.");
    return;
  }

  const grouped = groupBy(state.trendsByAge, "age_group");
  const cards = Object.entries(grouped).map(([ageGroup, items]) => {
    const profile = state.profilePredictions.find((entry) => entry.age_group === ageGroup);
    const image = profile?.products?.[0]?.image || state.sampleProducts[0]?.image || "";
    const tags = items.map((item) => `<span>${escapeHtml(item.style_category || item.category)}</span>`).join("");
    return `
      <article class="showcase-card">
        <img src="${escapeAttribute(image)}" alt="${escapeAttribute(ageGroup)} recommendation">
        <div class="showcase-copy">
          <p class="eyebrow">Age Segment</p>
          <h3>${escapeHtml(ageGroup)}</h3>
          <p>Top styles exported from the notebook for this fashion audience.</p>
          <div class="tag-list">${tags}</div>
        </div>
      </article>
    `;
  });

  container.innerHTML = cards.join("");
}

function renderOccasionShowcase() {
  const container = document.getElementById("occasionRecommendationGrid");
  if (!container) return;

  if (!state.trendsByOccasion.length) {
    container.innerHTML = createEmptyStateCard("Occasion-based recommendations will appear here after the exported data loads.");
    return;
  }

  const grouped = groupBy(state.trendsByOccasion, "occasion");
  const cards = Object.entries(grouped).map(([occasion, items]) => {
    const profile = state.profilePredictions.find((entry) => entry.occasion === occasion);
    const image = profile?.products?.[0]?.image || state.sampleProducts[0]?.image || "";
    const tags = items.map((item) => `<span>${escapeHtml(item.style_category || item.category)}</span>`).join("");
    return `
      <article class="showcase-card">
        <img src="${escapeAttribute(image)}" alt="${escapeAttribute(occasion)} fashion recommendation">
        <div class="showcase-copy">
          <p class="eyebrow">Occasion Focus</p>
          <h3>${escapeHtml(occasion)}</h3>
          <p>Most relevant styles for this wardrobe context in the exported data.</p>
          <div class="tag-list">${tags}</div>
        </div>
      </article>
    `;
  });

  container.innerHTML = cards.join("");
}

function renderShop() {
  const ageFilter = document.getElementById("ageFilter");
  const occasionFilter = document.getElementById("occasionFilter");
  const searchInput = document.getElementById("searchInput");
  const sortFilter = document.getElementById("sortFilter");
  const grid = document.getElementById("shopGrid");
  const meta = document.getElementById("shopMeta");

  if (!ageFilter || !occasionFilter || !searchInput || !sortFilter) return;

  if (!state.recommendations.length) {
    if (meta) meta.textContent = "No products loaded yet";
    if (grid) {
      grid.innerHTML = createEmptyStateCard("Start a local server to load the exported recommendation catalog.");
    }
    return;
  }

  uniqueValues(state.recommendations.map((item) => item.age_group)).forEach((value) => {
    ageFilter.insertAdjacentHTML("beforeend", `<option value="${escapeHtml(value)}">${escapeHtml(value)}</option>`);
  });
  uniqueValues(state.recommendations.map((item) => item.occasion)).forEach((value) => {
    occasionFilter.insertAdjacentHTML("beforeend", `<option value="${escapeHtml(value)}">${escapeHtml(value)}</option>`);
  });

  const render = () => {
    const query = searchInput.value.trim().toLowerCase();
    const ageValue = ageFilter.value;
    const occasionValue = occasionFilter.value;
    const sortValue = sortFilter.value;

    let items = [...state.recommendations].filter((item) => {
      const matchesQuery =
        !query ||
        String(item.name).toLowerCase().includes(query) ||
        String(item.brand).toLowerCase().includes(query) ||
        String(item.category).toLowerCase().includes(query);
      const matchesAge = ageValue === "all" || item.age_group === ageValue;
      const matchesOccasion = occasionValue === "all" || item.occasion === occasionValue;
      return matchesQuery && matchesAge && matchesOccasion;
    });

    items.sort((left, right) => {
      if (sortValue === "price_asc") return Number(left.price) - Number(right.price);
      if (sortValue === "price_desc") return Number(right.price) - Number(left.price);
      if (sortValue === "rating_desc") return Number(right.rating) - Number(left.rating);
      return Number(right.recommendation_score) - Number(left.recommendation_score);
    });

    if (meta) meta.textContent = `Showing ${items.length} products`;
    if (grid) {
      grid.innerHTML = items.length
        ? items.map((product) => createProductCard(product)).join("")
        : createEmptyStateCard("No products match the current filters.");
    }
  };

  render();
  [ageFilter, occasionFilter, searchInput, sortFilter].forEach((element) => {
    element.addEventListener("input", render);
    element.addEventListener("change", render);
  });
}

function initCartPage() {
  renderCartPage();
  renderCartSuggestions();
}

function renderCartPage() {
  const items = getCartItemsDetailed();
  const list = document.getElementById("cartItemsList");
  const subtotal = items.reduce((sum, item) => sum + item.line_total, 0);
  const count = items.reduce((sum, item) => sum + item.quantity, 0);

  setText("cartItemCount", String(count));
  setText("cartSubtotal", formatCurrency(subtotal));

  if (!list) return;
  if (!items.length) {
    list.innerHTML = `
      <article class="empty-card">
        <h3>Your cart is empty</h3>
        <p>Add products from the homepage to continue your fashion checkout flow.</p>
        <a class="button button-primary" href="./index.html#shop">Start Shopping</a>
      </article>
    `;
    return;
  }

  list.innerHTML = items.map((item) => createCartItemCard(item)).join("");
}

function renderCartSuggestions() {
  const container = document.getElementById("cartSuggestions");
  if (!container) return;
  const items = state.recommendations.slice(0, 4);
  if (!items.length) {
    container.innerHTML = createEmptyStateCard("Recommendation suggestions will appear here once the exported data loads.");
    return;
  }
  container.innerHTML = items.map((product) => createProductCard(product)).join("");
}

function initCheckoutPage() {
  renderCheckoutSummary();
  document.getElementById("checkoutForm")?.addEventListener("submit", handleCheckout);
}

function renderCheckoutSummary() {
  const items = getCartItemsDetailed();
  const container = document.getElementById("checkoutItems");
  const total = items.reduce((sum, item) => sum + item.line_total, 0);
  const count = items.reduce((sum, item) => sum + item.quantity, 0);

  setText("checkoutItemCount", String(count));
  setText("checkoutTotal", formatCurrency(total));

  if (!container) return;
  if (!items.length) {
    container.innerHTML = `
      <article class="empty-card">
        <p>No items are in the cart yet.</p>
        <a class="button button-secondary" href="./index.html#shop">Go Back To Shop</a>
      </article>
    `;
    return;
  }

  container.innerHTML = items
    .map((item) => {
      return `
        <article class="cart-item-card">
          <img src="${escapeAttribute(item.image)}" alt="${escapeAttribute(item.name)}">
          <div class="cart-item-copy">
            <h3>${escapeHtml(item.name)}</h3>
            <p>${escapeHtml(item.brand || "Fashion Pick")} • ${escapeHtml(item.category || "Style")}</p>
            <p>${formatCurrency(item.price)} x ${item.quantity}</p>
          </div>
        </article>
      `;
    })
    .join("");
}

function handleCheckout(event) {
  event.preventDefault();
  const items = getCartItemsDetailed();
  const message = document.getElementById("checkoutMessage");
  if (!items.length) {
    if (message) {
      message.textContent = "Add at least one product before placing a demo order.";
      message.classList.remove("status-text");
    }
    return;
  }

  state.cart = [];
  saveCart();
  updateCartCount();
  renderCheckoutSummary();

  if (message) {
    message.textContent = "Demo order placed successfully. The cart has been cleared for your next showcase.";
    message.classList.add("status-text");
  }

  event.target.reset();
}

function bindGlobalEvents() {
  document.body.addEventListener("click", (event) => {
    const addButton = event.target.closest("[data-add-to-cart]");
    if (addButton) {
      addToCart(addButton.dataset.addToCart);
      return;
    }

    const quantityButton = event.target.closest("[data-quantity-key]");
    if (quantityButton) {
      changeQuantity(quantityButton.dataset.quantityKey, Number(quantityButton.dataset.quantityDelta));
      renderCartPage();
      renderCheckoutSummary();
      return;
    }

    const removeButton = event.target.closest("[data-remove-key]");
    if (removeButton) {
      removeFromCart(removeButton.dataset.removeKey);
      renderCartPage();
      renderCheckoutSummary();
    }
  });
}

function createProductCard(product) {
  const safeProduct = normalizeProduct(product);
  const key = buildProductKey(product);
  const tags = (safeProduct.reason_tags || [])
    .slice(0, 3)
    .map((tag) => `<span>${escapeHtml(tag)}</span>`)
    .join("");

  return `
    <article class="product-card">
      <img src="${escapeAttribute(safeProduct.image)}" alt="${escapeAttribute(safeProduct.name)}" loading="lazy">
      <div class="product-copy">
        <div class="product-meta">
          <span>${escapeHtml(safeProduct.category || "Style")}</span>
          <span>${escapeHtml(safeProduct.occasion || "Occasion")}</span>
        </div>
        <h3>${escapeHtml(safeProduct.name)}</h3>
        <p>${escapeHtml(safeProduct.brand || "Fashion Brand")} • ${escapeHtml(safeProduct.age_group || "Women")}</p>
        <div class="tag-list">${tags}</div>
        <div class="product-footer">
          <span class="price-line">${formatCurrency(safeProduct.price)}</span>
          <button class="button button-primary" data-add-to-cart="${escapeAttribute(key)}">Add To Cart</button>
        </div>
      </div>
    </article>
  `;
}

function createMiniCard(product, ageGroup, occasion) {
  const merged = normalizeProduct({ ...product, age_group: ageGroup, occasion });
  const key = buildProductKey(merged);
  return `
    <article class="mini-card product-card">
      <img src="${escapeAttribute(merged.image)}" alt="${escapeAttribute(merged.name)}" loading="lazy">
      <div class="mini-copy">
        <h4>${escapeHtml(merged.name)}</h4>
        <p>${escapeHtml(merged.brand || "Fashion Brand")} • ${formatCurrency(merged.price)}</p>
        <div class="product-footer">
          <span class="price-line">Rating ${Number(merged.rating || 0).toFixed(1)}</span>
          <button class="button button-primary" data-add-to-cart="${escapeAttribute(key)}">Add To Cart</button>
        </div>
      </div>
    </article>
  `;
}

function createCartItemCard(item) {
  const safeItem = normalizeProduct(item);
  return `
    <article class="cart-item-card">
      <img src="${escapeAttribute(safeItem.image)}" alt="${escapeAttribute(safeItem.name)}" loading="lazy">
      <div class="cart-item-copy">
        <div class="cart-item-main">
          <h3>${escapeHtml(safeItem.name)}</h3>
          <button class="remove-button" data-remove-key="${escapeAttribute(safeItem.key)}">Remove</button>
        </div>
        <p>${escapeHtml(safeItem.brand || "Fashion Brand")} • ${escapeHtml(safeItem.category || "Style")} • ${escapeHtml(safeItem.occasion || "Occasion")}</p>
        <p>${formatCurrency(safeItem.price)} each • Line total ${formatCurrency(item.line_total)}</p>
        <div class="quantity-control">
          <button class="quantity-button" data-quantity-key="${escapeAttribute(safeItem.key)}" data-quantity-delta="-1">-</button>
          <span>${item.quantity}</span>
          <button class="quantity-button" data-quantity-key="${escapeAttribute(safeItem.key)}" data-quantity-delta="1">+</button>
        </div>
      </div>
    </article>
  `;
}

function createEmptyStateCard(message) {
  return `
    <article class="empty-card">
      <p>${escapeHtml(message)}</p>
    </article>
  `;
}

function groupBy(items, field) {
  return items.reduce((accumulator, item) => {
    const key = item[field];
    if (!accumulator[key]) accumulator[key] = [];
    accumulator[key].push(item);
    return accumulator;
  }, {});
}

function uniqueValues(values) {
  return Array.from(new Set(values.filter(Boolean)));
}

function setText(id, value) {
  const element = document.getElementById(id);
  if (element) element.textContent = value;
}

function escapeHtml(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/\"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function escapeAttribute(value) {
  return escapeHtml(value);
}
