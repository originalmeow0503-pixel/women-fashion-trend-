const STORAGE_KEY = "trendmuse_cart_v1";
const DEFAULT_PRODUCT_IMAGE = "assets/images/hero-banner.svg";
const LOCAL_API_BASE_URL = "http://127.0.0.1:5000";
const PREDICTION_API_BASE_URL = ["localhost", "127.0.0.1"].includes(window.location.hostname)
  ? LOCAL_API_BASE_URL
  : "";
const STYLE_PREFERENCE_CONFIG = {
  no_preference: {
    label: "No specific preference",
    titlePrefix: "Balanced",
    explanation: "without a strong colour preference",
    keywords: [],
    fallbackSort: "recommendation_score",
  },
  soft_neutrals: {
    label: "Soft neutrals",
    titlePrefix: "Soft Neutral",
    explanation: "with lighter neutral shades such as cream, beige, and nude",
    keywords: ["white", "off white", "cream", "beige", "nude", "taupe", "brown", "camel", "peach"],
    fallbackSort: "price_asc",
  },
  bold_colours: {
    label: "Bold colours",
    titlePrefix: "Bold Colour",
    explanation: "with brighter shades such as pink, red, orange, and coral",
    keywords: ["pink", "fuchsia", "red", "orange", "coral", "magenta", "yellow"],
    fallbackSort: "recommendation_score",
  },
  cool_tones: {
    label: "Cool tones",
    titlePrefix: "Cool Tone",
    explanation: "with calmer blue and green shades",
    keywords: ["blue", "green", "teal", "turquoise", "lavender", "navy", "olive"],
    fallbackSort: "name_asc",
  },
  classic_darks: {
    label: "Classic darks",
    titlePrefix: "Classic Dark",
    explanation: "with deeper shades such as black, navy, maroon, and grey",
    keywords: ["black", "grey", "gray", "navy", "maroon", "purple", "charcoal"],
    fallbackSort: "rating_desc",
  },
  festive_metallics: {
    label: "Festive metallics",
    titlePrefix: "Festive Metallic",
    explanation: "with gold, silver, bronze, or champagne tones",
    keywords: ["gold", "silver", "bronze", "champagne", "copper", "rose gold"],
    fallbackSort: "price_desc",
  },
};
const STYLE_FALLBACK_SORTERS = {
  recommendation_score: (left, right) => Number(right.recommendation_score || 0) - Number(left.recommendation_score || 0),
  rating_desc: (left, right) => Number(right.rating || 0) - Number(left.rating || 0),
  price_asc: (left, right) => Number(left.price || 0) - Number(right.price || 0),
  price_desc: (left, right) => Number(right.price || 0) - Number(left.price || 0),
  name_asc: (left, right) => String(left.name || "").localeCompare(String(right.name || "")),
};
const CHATBOT_OCCASION_RULES = [
  { occasion: "Wedding", pattern: /(wedding|bridal|bride|ceremony|reception)/ },
  { occasion: "Party", pattern: /(party|evening|night out|cocktail)/ },
  { occasion: "Office", pattern: /(office|work|formal|meeting)/ },
  { occasion: "Festive", pattern: /(festive|festival|ethnic|traditional|puja|diwali)/ },
  { occasion: "Vacation", pattern: /(vacation|travel|trip|holiday|beach)/ },
  { occasion: "Daily Wear", pattern: /(daily wear|everyday|regular wear)/ },
  { occasion: "Casual", pattern: /(college|campus|class|casual)/ },
];
const CHATBOT_CATEGORY_RULES = [
  { category: "Dresses", pattern: /(dress|dresses|gown|gowns)/, fallbackCategories: ["Dresses", "Sarees", "Ethnic Sets", "Traditional Wear", "Co-ord Sets"] },
  { category: "Sarees", pattern: /(saree|sarees)/, fallbackCategories: ["Sarees", "Traditional Wear", "Ethnic Sets"] },
  { category: "Ethnic Sets", pattern: /(ethnic set|ethnic sets|lehenga|lehengas|sharara|salwar set|anarkali)/, fallbackCategories: ["Ethnic Sets", "Traditional Wear", "Sarees"] },
  { category: "Kurtis & Kurtas", pattern: /(kurti|kurtis|kurta|kurtas)/, fallbackCategories: ["Kurtis & Kurtas", "Ethnic Sets"] },
  { category: "Co-ord Sets", pattern: /(co-ord|coord|co ord|matching set)/, fallbackCategories: ["Co-ord Sets", "Tops"] },
  { category: "Tops", pattern: /(top|tops|blouse|blouses|shirt|shirts)/, fallbackCategories: ["Tops", "Co-ord Sets"] },
  { category: "Bottom Wear", pattern: /(bottom|bottoms|jeans|trousers|pants|palazzo|palazzos|skirt|skirts)/, fallbackCategories: ["Bottom Wear", "Co-ord Sets"] },
  { category: "Traditional Wear", pattern: /(traditional wear|traditional|ethnic wear)/, fallbackCategories: ["Traditional Wear", "Ethnic Sets", "Sarees"] },
];
const CHATBOT_STOPWORDS = new Set([
  "a",
  "an",
  "and",
  "any",
  "best",
  "can",
  "for",
  "from",
  "give",
  "help",
  "i",
  "in",
  "is",
  "like",
  "look",
  "me",
  "my",
  "need",
  "of",
  "on",
  "outfit",
  "outfits",
  "please",
  "recommend",
  "show",
  "some",
  "suggest",
  "the",
  "to",
  "want",
  "wear",
  "with",
]);
const STATIC_MEN_PRODUCTS = [
  {
    product_id: "men-structured-blazer",
    name: "Structured Blazer",
    brand: "E-SHINE Men",
    category: "Blazers",
    age_group: "Men",
    occasion: "Formal",
    price: 3299,
    rating: 4.6,
    recommendation_score: 0.91,
    image: "https://www.crimsouneclub.com/cdn/shop/files/UntitledSession03249_1080x.jpg?v=1754568629",
    description: "Clean tailoring and sharper evening styling from the old project reference.",
  },
  {
    product_id: "men-festive-kurta-set",
    name: "Festive Kurta Set",
    brand: "E-SHINE Men",
    category: "Kurta Sets",
    age_group: "Men",
    occasion: "Festive",
    price: 2899,
    rating: 4.5,
    recommendation_score: 0.88,
    image: "https://medias.utsavfashion.com/media/catalog/product/cache/1/small_image/295x/040ec09b1e35df139433887a97daa66f/w/o/woven-viscose-rayon-jacquard-kurta-set-in-cream-v1-mnr217.jpg",
    description: "A softer festive direction that mirrors the older catalogue layout without changing the project logic.",
  },
  {
    product_id: "men-wedding-sherwani",
    name: "Wedding Sherwani",
    brand: "E-SHINE Men",
    category: "Sherwanis",
    age_group: "Men",
    occasion: "Wedding",
    price: 8499,
    rating: 4.8,
    recommendation_score: 0.94,
    image: "https://i.etsystatic.com/34650355/r/il/a2ce99/4020929058/il_fullxfull.4020929058_gefl.jpg",
    description: "Richer ceremonial styling included here to preserve the page variety from the older project.",
  },
  {
    product_id: "men-formal-shirt",
    name: "Formal Shirt",
    brand: "E-SHINE Men",
    category: "Shirts",
    age_group: "Men",
    occasion: "Office",
    price: 1799,
    rating: 4.4,
    recommendation_score: 0.84,
    image: "https://m.media-amazon.com/images/I/41k8b5UDbML._AC_UY1100_.jpg",
    description: "Simple officewear styling that keeps the page grounded and easy to scan in a presentation.",
  },
  {
    product_id: "men-classic-sherwani",
    name: "Classic Sherwani",
    brand: "E-SHINE Men",
    category: "Sherwanis",
    age_group: "Men",
    occasion: "Ceremony",
    price: 7999,
    rating: 4.7,
    recommendation_score: 0.9,
    image: "https://www.nihalfashions.com/media/catalog/product/cache/caa15edf98145413286703527de7b8dd/l/i/light-brown-art-silk-mens-sherwani-nmk-6875.jpg",
    description: "A ceremonial reference card that carries the same structured product-grid treatment.",
  },
  {
    product_id: "men-tailored-waistcoat",
    name: "Tailored Waistcoat",
    brand: "E-SHINE Men",
    category: "Waistcoats",
    age_group: "Men",
    occasion: "Smart",
    price: 2599,
    rating: 4.3,
    recommendation_score: 0.82,
    image: "https://static.fursac.com/data/waistcoat-men-3-piece-suit-taupe-brown-g3bilg-gc17-a008-pl3133166.1749824406.jpg",
    description: "A bridge between formal and occasion dressing, used here as a design reference card.",
  },
  {
    product_id: "men-coat-and-pant",
    name: "Coat And Pant",
    brand: "E-SHINE Men",
    category: "Suits",
    age_group: "Men",
    occasion: "Formal",
    price: 4199,
    rating: 4.5,
    recommendation_score: 0.86,
    image: "https://i.pinimg.com/originals/51/39/51/5139510b643681466e6129df18fe82bf.jpg",
    description: "The clean storefront presentation is the part being borrowed here, not the older project logic.",
  },
  {
    product_id: "men-formal-pant",
    name: "Formal Pant",
    brand: "E-SHINE Men",
    category: "Trousers",
    age_group: "Men",
    occasion: "Workwear",
    price: 1499,
    rating: 4.2,
    recommendation_score: 0.8,
    image: "https://www.sainly.com/cdn/shop/products/sainly-apparel-accessories-26-men-pants-office-grey-casual-straight-suit-pants-men-s-formal-pants-men-s-dress-party-club-dress-pants-men-office-grey-casual-men-formal-pants-men-party.png?v=1663244657",
    description: "A quieter wardrobe basic that helps this linked page feel complete without becoming the main feature.",
  },
];
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
  } else if (page === "women") {
    initWomenPage();
  } else if (page === "cart") {
    initCartPage();
  } else if (page === "checkout") {
    initCheckoutPage();
  }

  initFashionChatbot();

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

  STATIC_MEN_PRODUCTS.map(normalizeProduct).forEach((product) => {
    const key = buildProductKey(product);
    if (!map.has(key)) {
      map.set(key, { ...product, key });
    }
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
}

function initWomenPage() {
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
  const categorySelect = document.getElementById("categorySelect");
  const stylePreferenceSelect = document.getElementById("stylePreference");
  const profileForm = document.getElementById("profileForm");
  const submitButton = document.querySelector('#profileForm button[type="submit"]');
  if (!ageSelect || !occasionSelect || !categorySelect || !stylePreferenceSelect || !profileForm) return;

  const ageGroups = uniqueValues(state.profilePredictions.map((item) => item.age_group));
  const occasions = uniqueValues(state.profilePredictions.map((item) => item.occasion));

  if (!ageGroups.length || !occasions.length) {
    ageSelect.innerHTML = '<option value="">Local server required</option>';
    occasionSelect.innerHTML = '<option value="">JSON data required</option>';
    categorySelect.innerHTML = '<option value="">No categories available</option>';
    stylePreferenceSelect.innerHTML = '<option value="">No style preferences available</option>';
    ageSelect.disabled = true;
    occasionSelect.disabled = true;
    categorySelect.disabled = true;
    stylePreferenceSelect.disabled = true;
    if (submitButton) submitButton.disabled = true;
    setText("resultPill", "Awaiting Data");
    setText("resultCategory", "Exported results not loaded");
    setText("resultSummary", "Start a local server to load the exported profile predictions and recommendation cards.");
    setText("resultAge", "--");
    setText("resultOccasion", "--");
    setText("resultScore", "--");
    setText("resultStyle", "--");
    const container = document.getElementById("predictionProducts");
    if (container) {
      container.innerHTML = createEmptyStateCard("Profile-based product matches will appear here after the JSON files load.");
    }
    return;
  }

  ageSelect.innerHTML = ageGroups.map((value) => `<option value="${escapeHtml(value)}">${escapeHtml(value)}</option>`).join("");
  occasionSelect.innerHTML = occasions.map((value) => `<option value="${escapeHtml(value)}">${escapeHtml(value)}</option>`).join("");
  stylePreferenceSelect.innerHTML = Object.entries(STYLE_PREFERENCE_CONFIG)
    .map(([value, config]) => `<option value="${escapeHtml(value)}">${escapeHtml(config.label)}</option>`)
    .join("");
  ageSelect.disabled = false;
  occasionSelect.disabled = false;
  stylePreferenceSelect.disabled = false;
  if (submitButton) submitButton.disabled = false;

  const syncCategoryOptions = () => {
    populateCategoryOptions(ageSelect.value, occasionSelect.value, categorySelect.value);
  };

  const updateProfileResult = async () => {
    await requestProfileResult(
      ageSelect.value,
      occasionSelect.value,
      categorySelect.value,
      stylePreferenceSelect.value,
    );
  };

  syncCategoryOptions();
  updateProfileResult();

  profileForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    await updateProfileResult();
  });

  [ageSelect, occasionSelect].forEach((element) => {
    element.addEventListener("change", () => {
      syncCategoryOptions();
      updateProfileResult();
    });
  });

  [categorySelect, stylePreferenceSelect].forEach((element) => {
    element.addEventListener("change", updateProfileResult);
  });
}

async function requestProfileResult(ageGroup, occasion, category, stylePreference) {
  const apiResponse = await fetchPredictionFromApi({
    ageGroup,
    occasion,
    category,
    stylePreference,
  });

  if (apiResponse) {
    renderProfileResultFromApi(apiResponse, ageGroup, occasion);
    return;
  }

  renderProfileResult(ageGroup, occasion, category, stylePreference);
}

async function fetchPredictionFromApi(payload) {
  if (!PREDICTION_API_BASE_URL) return null;

  try {
    const response = await fetch(`${PREDICTION_API_BASE_URL}/predict`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      throw new Error("Prediction API request failed");
    }

    return await response.json();
  } catch (error) {
    return null;
  }
}

function renderProfileResultFromApi(result, ageGroup, occasion) {
  const products = Array.isArray(result?.products) ? result.products : [];
  const score = typeof result?.score === "number" ? result.score.toFixed(3) : "--";
  const styleImpact = {
    label: result?.style_impact || "Assisted Ranking",
    note: result?.style_impact_note || "The result follows the current ranking flow for this profile.",
    tone: getStyleImpactTone(result?.style_impact),
  };

  setText("resultPill", getTrendLabelFromScore(Number(result?.score || 0)));
  setText("resultCategory", result?.recommended_style || "Style Match");
  setText("resultSummary", result?.summary || "This recommendation comes from the backend API response.");
  setText("resultAge", ageGroup || "--");
  setText("resultOccasion", occasion || "--");
  setText("resultScore", score);
  setText("resultStyle", result?.style_preference || "No specific preference");
  setStyleImpactIndicator(styleImpact);

  const resultCard = document.getElementById("profileResultCard") || document.querySelector(".result-card");
  if (resultCard) resultCard.hidden = false;

  const container = document.getElementById("predictionProducts");
  if (container) {
    container.innerHTML = products.length
      ? products.map((product) => createMiniCard(product, ageGroup, occasion)).join("")
      : createEmptyStateCard("No products match the selected profile.");
  }
}

function getTrendLabelFromScore(score) {
  if (score >= 0.75) return "High Trend";
  if (score >= 0.55) return "Rising Trend";
  return "Niche Trend";
}

function getStyleImpactTone(label) {
  if (label === "Strong Style Match") return "strong";
  if (label === "Partial Style Match") return "partial";
  return "fallback";
}

function populateCategoryOptions(ageGroup, occasion, selectedCategory = "") {
  const categorySelect = document.getElementById("categorySelect");
  if (!categorySelect) return [];

  const categories = getCategoryOptions(ageGroup, occasion);
  if (!categories.length) {
    categorySelect.innerHTML = '<option value="">No categories available</option>';
    categorySelect.disabled = true;
    return [];
  }

  categorySelect.innerHTML = categories
    .map((value) => `<option value="${escapeHtml(value)}">${escapeHtml(value)}</option>`)
    .join("");
  categorySelect.disabled = false;
  categorySelect.value = categories.includes(selectedCategory) ? selectedCategory : categories[0];
  return categories;
}

function getCategoryOptions(ageGroup, occasion) {
  const categories = new Set();

  state.profilePredictions
    .filter((item) => item.age_group === ageGroup && item.occasion === occasion)
    .forEach((profile) => {
      if (profile.predicted_style) categories.add(profile.predicted_style);
      (profile.products || []).forEach((product) => {
        if (product.category) categories.add(product.category);
      });
    });

  state.recommendations
    .filter((item) => item.age_group === ageGroup && item.occasion === occasion)
    .forEach((item) => {
      if (item.category) categories.add(item.category);
    });

  return Array.from(categories);
}

function renderProfileResult(ageGroup, occasion, category, stylePreference) {
  const profile = state.profilePredictions.find((item) => item.age_group === ageGroup && item.occasion === occasion);
  const styleConfig = getStylePreferenceConfig(stylePreference);
  const matchingProducts = getProfileProducts(ageGroup, occasion, category);
  if (!profile && !matchingProducts.length) return;

  const rankedProducts = rankProductsByStyle(matchingProducts, styleConfig).slice(0, 4);
  const averageScore = rankedProducts.length
    ? rankedProducts.reduce((sum, product) => sum + Number(product._matchScore || 0), 0) / rankedProducts.length
    : Number(profile?.trend_score || 0);
  const label = averageScore >= 0.75 ? "High Trend" : averageScore >= 0.55 ? "Rising Trend" : "Niche Trend";
  const titleCategory = category || profile?.predicted_style || "Style Match";
  const resultTitle = styleConfig.keywords.length
    ? `${styleConfig.titlePrefix} ${titleCategory}`
    : titleCategory;
  const styleImpact = getStyleImpact(rankedProducts, styleConfig);

  setText("resultPill", label);
  setText("resultCategory", resultTitle);
  setText("resultSummary", buildProfileExplanation(profile, titleCategory, styleConfig, rankedProducts));
  setText("resultAge", ageGroup || profile?.age_group || "--");
  setText("resultOccasion", occasion || profile?.occasion || "--");
  setText("resultScore", averageScore.toFixed(3));
  setText("resultStyle", styleConfig.label);
  setStyleImpactIndicator(styleImpact);

  const resultCard = document.getElementById("profileResultCard") || document.querySelector(".result-card");
  if (resultCard) resultCard.hidden = false;

  const container = document.getElementById("predictionProducts");
  if (container) {
    container.innerHTML = rankedProducts.length
      ? rankedProducts.map((product) => createMiniCard(product, ageGroup, occasion)).join("")
      : createEmptyStateCard("No products match the selected profile.");
  }
}

function getStylePreferenceConfig(stylePreference) {
  return STYLE_PREFERENCE_CONFIG[stylePreference] || STYLE_PREFERENCE_CONFIG.no_preference;
}

function getProfileProducts(ageGroup, occasion, category) {
  const profile = state.profilePredictions.find((item) => item.age_group === ageGroup && item.occasion === occasion);
  const profileProducts = (profile?.products || []).filter((product) => !category || product.category === category);
  const recommendationProducts = state.recommendations.filter((item) => {
    const matchesAge = item.age_group === ageGroup;
    const matchesOccasion = item.occasion === occasion;
    const matchesCategory = !category || item.category === category;
    return matchesAge && matchesOccasion && matchesCategory;
  });

  const merged = new Map();
  [...profileProducts, ...recommendationProducts].forEach((product) => {
    const key = buildProductKey(product);
    if (!merged.has(key)) {
      merged.set(key, normalizeProduct(product));
    }
  });

  return Array.from(merged.values());
}

function rankProductsByStyle(products, styleConfig) {
  const sortByFallback = STYLE_FALLBACK_SORTERS[styleConfig.fallbackSort] || STYLE_FALLBACK_SORTERS.recommendation_score;

  return [...products]
    .map((product) => {
      const haystack = [
        product.colour,
        product.name,
        product.description,
        product.brand,
      ]
        .filter(Boolean)
        .join(" ")
        .toLowerCase();
      const styleMatchCount = styleConfig.keywords.reduce((count, keyword) => {
        return haystack.includes(keyword) ? count + 1 : count;
      }, 0);
      const baseScore = Number(product.recommendation_score || product.trend_score || 0);
      const styleBoost = styleConfig.keywords.length ? styleMatchCount * 0.03 : 0;

      return {
        ...product,
        _styleMatchCount: styleMatchCount,
        _matchScore: baseScore + styleBoost,
      };
    })
    .sort((left, right) => {
      if (right._styleMatchCount !== left._styleMatchCount) {
        return right._styleMatchCount - left._styleMatchCount;
      }
      const fallbackOrder = sortByFallback(left, right);
      if (styleConfig.keywords.length && fallbackOrder !== 0) {
        return fallbackOrder;
      }
      if (right._matchScore !== left._matchScore) {
        return right._matchScore - left._matchScore;
      }
      return fallbackOrder;
    });
}

function buildProfileExplanation(profile, category, styleConfig, rankedProducts) {
  const matchedItems = rankedProducts.filter((product) => product._styleMatchCount > 0).length;
  const baseSummary = profile?.summary
    || `${category} is the closest match for the selected age group and occasion in the exported project data.`;
  const categorySentence = category ? ` This view is focused on ${category.toLowerCase()}.` : "";
  const styleSentence = !styleConfig.keywords.length
    ? "The list is ordered by the main recommendation score for this profile."
    : matchedItems
      ? `${matchedItems} of the top items also align with the ${styleConfig.label.toLowerCase()} preference.`
      : `The selected preference does not appear directly in the top items, so the list is softly re-ranked for a ${styleConfig.label.toLowerCase()} direction.`;

  return `${baseSummary}${categorySentence} ${styleSentence}`;
}

function getStyleImpact(rankedProducts, styleConfig) {
  const totalItems = rankedProducts.length;
  const matchedItems = rankedProducts.filter((product) => product._styleMatchCount > 0).length;

  if (!styleConfig.keywords.length) {
    return {
      label: "Assisted Ranking",
      note: "No specific style preference was selected, so the result is ordered using the main recommendation score for this profile.",
      tone: "fallback",
    };
  }

  if (matchedItems >= Math.max(2, Math.ceil(totalItems / 2))) {
    return {
      label: "Strong Style Match",
      note: `${matchedItems} of the top ${totalItems} items align clearly with the selected style preference.`,
      tone: "strong",
    };
  }

  if (matchedItems > 0) {
    return {
      label: "Partial Style Match",
      note: `${matchedItems} of the top ${totalItems} items align with the selected style preference, while the final order still reflects the general recommendation score.`,
      tone: "partial",
    };
  }

  return {
    label: "Assisted Ranking",
    note: `The selected ${styleConfig.label.toLowerCase()} preference was not strongly present in the top items, so a style-aware re-ranking was used for this profile.`,
    tone: "fallback",
  };
}

function setStyleImpactIndicator(styleImpact) {
  const label = document.getElementById("resultImpactLabel");
  const note = document.getElementById("resultImpactNote");

  if (label) {
    label.textContent = styleImpact.label;
    label.dataset.impact = styleImpact.tone;
  }

  if (note) {
    note.textContent = styleImpact.note;
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

  const initialFilters = getShopFiltersFromUrl();
  if (initialFilters.search) searchInput.value = initialFilters.search;
  if (hasSelectOption(ageFilter, initialFilters.age)) ageFilter.value = initialFilters.age;
  if (hasSelectOption(occasionFilter, initialFilters.occasion)) occasionFilter.value = initialFilters.occasion;
  if (hasSelectOption(sortFilter, initialFilters.sort)) sortFilter.value = initialFilters.sort;

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

function getShopFiltersFromUrl() {
  const params = new URLSearchParams(window.location.search);
  return {
    search: params.get("search") || "",
    age: params.get("age") || "all",
    occasion: params.get("occasion") || "all",
    sort: params.get("sort") || "trend_desc",
  };
}

function hasSelectOption(select, value) {
  return Boolean(value) && Array.from(select.options).some((option) => option.value === value);
}

function parseChatbotIntent(message) {
  const normalizedMessage = String(message || "").toLowerCase();
  const occasionRule = CHATBOT_OCCASION_RULES.find((rule) => rule.pattern.test(normalizedMessage));
  const categoryRule = CHATBOT_CATEGORY_RULES.find((rule) => rule.pattern.test(normalizedMessage));
  const stylePreference = getChatbotStylePreferenceKey(normalizedMessage);

  return {
    message: normalizedMessage,
    occasion: occasionRule?.occasion || "",
    category: categoryRule?.category || "",
    categoryFallbacks: categoryRule?.fallbackCategories || [],
    stylePreference,
    styleConfig: getStylePreferenceConfig(stylePreference),
    keywords: extractChatbotKeywords(normalizedMessage),
  };
}

function getChatbotStylePreferenceKey(message) {
  const normalizedMessage = String(message || "").toLowerCase();
  const entry = Object.entries(STYLE_PREFERENCE_CONFIG).find(([key, config]) => {
    if (key === "no_preference") return false;
    if (normalizedMessage.includes(config.label.toLowerCase())) return true;
    return config.keywords.some((keyword) => normalizedMessage.includes(keyword));
  });

  return entry?.[0] || "no_preference";
}

function extractChatbotKeywords(message) {
  const words = String(message || "").toLowerCase().match(/[a-z]+/g) || [];
  return uniqueValues(
    words.filter((word) => word.length > 2 && !CHATBOT_STOPWORDS.has(word)),
  );
}

function buildChatbotResponse(message) {
  const intent = parseChatbotIntent(message);
  const wantsRecommendations =
    Boolean(intent.occasion)
    || Boolean(intent.category)
    || intent.stylePreference !== "no_preference"
    || /(suggest|recommend|show|find|need|wear|look|style|shopping)/.test(intent.message);

  if (wantsRecommendations) {
    const recommendationResult = getChatbotRecommendations(intent);
    if (recommendationResult.products.length) {
      return {
        text: buildChatbotRecommendationText(intent, recommendationResult),
        products: recommendationResult.products,
      };
    }
  }

  return {
    text: getChatbotReply(message),
    products: [],
  };
}

function getChatbotRecommendations(intent) {
  const catalog = state.recommendations.length ? state.recommendations : state.sampleProducts;
  if (!catalog.length) {
    return { products: [], usedCategoryFallback: false };
  }

  let pool = [...catalog];

  if (intent.occasion) {
    const occasionMatches = pool.filter((product) => product.occasion === intent.occasion);
    if (occasionMatches.length) {
      pool = occasionMatches;
    }
  }

  let usedCategoryFallback = false;
  if (intent.category) {
    const exactCategoryMatches = pool.filter((product) => product.category === intent.category);
    if (exactCategoryMatches.length) {
      pool = exactCategoryMatches;
    } else if (intent.categoryFallbacks.length) {
      const fallbackMatches = pool.filter((product) => intent.categoryFallbacks.includes(product.category));
      if (fallbackMatches.length) {
        pool = fallbackMatches;
        usedCategoryFallback = true;
      }
    }
  }

  return {
    products: rankChatbotProducts(pool, intent).slice(0, 3),
    usedCategoryFallback,
  };
}

function rankChatbotProducts(products, intent) {
  return rankProductsByStyle(products, intent.styleConfig)
    .map((product) => {
      const haystack = [
        product.name,
        product.description,
        product.brand,
        product.colour,
        product.category,
        product.occasion,
      ]
        .filter(Boolean)
        .join(" ")
        .toLowerCase();
      const keywordHits = intent.keywords.reduce((count, keyword) => {
        return haystack.includes(keyword) ? count + 1 : count;
      }, 0);
      const categoryBoost = intent.category && product.category === intent.category ? 0.08 : 0;
      const occasionBoost = intent.occasion && product.occasion === intent.occasion ? 0.06 : 0;
      const keywordBoost = keywordHits * 0.03;
      const baseScore = Number(product._matchScore || product.recommendation_score || product.trend_score || 0);

      return {
        ...product,
        _chatbotScore: baseScore + categoryBoost + occasionBoost + keywordBoost,
        _chatbotKeywordHits: keywordHits,
      };
    })
    .sort((left, right) => {
      if (right._chatbotScore !== left._chatbotScore) {
        return right._chatbotScore - left._chatbotScore;
      }
      if (right._chatbotKeywordHits !== left._chatbotKeywordHits) {
        return right._chatbotKeywordHits - left._chatbotKeywordHits;
      }
      return Number(right.recommendation_score || 0) - Number(left.recommendation_score || 0);
    });
}

function buildChatbotRecommendationText(intent, recommendationResult) {
  const { products, usedCategoryFallback } = recommendationResult;
  const styleSuffix = intent.stylePreference !== "no_preference"
    ? ` with a ${intent.styleConfig.label.toLowerCase()} feel`
    : "";

  if (intent.occasion && intent.category && usedCategoryFallback) {
    return `I could not find exact ${intent.category.toLowerCase()} for ${intent.occasion.toLowerCase()} in the current catalog, so here are the closest ${intent.occasion.toLowerCase()} picks${styleSuffix}. Click any image to open it in the Women shop page.`;
  }

  if (intent.occasion && intent.category) {
    return `Here are ${products.length} ${intent.occasion.toLowerCase()} ${intent.category.toLowerCase()} picks from your website${styleSuffix}. Click any image to open it in the Women shop page.`;
  }

  if (intent.occasion) {
    return `Here are ${products.length} ${intent.occasion.toLowerCase()} recommendations from your website${styleSuffix}. Click any image to open it in the Women shop page.`;
  }

  if (intent.category) {
    return `Here are ${products.length} ${intent.category.toLowerCase()} picks from your website${styleSuffix}. Click any image to open it in the Women shop page.`;
  }

  return `Here are ${products.length} style picks from your website${styleSuffix}. Click any image to open it in the Women shop page.`;
}

function buildChatbotShopUrl(product) {
  const safeProduct = normalizeProduct(product);
  const params = new URLSearchParams();
  params.set("search", safeProduct.name || "");
  if (safeProduct.age_group) params.set("age", safeProduct.age_group);
  if (safeProduct.occasion) params.set("occasion", safeProduct.occasion);
  params.set("sort", "trend_desc");
  return `./women.html?${params.toString()}#shop`;
}

function createChatbotProductCardMarkup(product) {
  const safeProduct = normalizeProduct(product);
  return `
    <a class="chatbot-product-link" href="${escapeAttribute(buildChatbotShopUrl(safeProduct))}">
      <img src="${escapeAttribute(safeProduct.image)}" alt="${escapeAttribute(safeProduct.name)}" loading="lazy">
      <span class="chatbot-product-copy">
        <strong>${escapeHtml(safeProduct.name)}</strong>
        <span>${escapeHtml(safeProduct.category || "Style")} • ${formatCurrency(safeProduct.price)}</span>
        <span>${escapeHtml(safeProduct.occasion || "Occasion")} • ${escapeHtml(safeProduct.brand || "Fashion Brand")}</span>
        <em>Open in Women shop</em>
      </span>
    </a>
  `;
}

function initFashionChatbot() {
  const launcher = document.getElementById("chatbotLauncher");
  const panel = document.getElementById("chatbotPanel");
  const form = document.getElementById("chatbotForm");
  const input = document.getElementById("chatbotInput");
  const messages = document.getElementById("chatbotMessages");
  const clearButton = document.getElementById("chatbotClear");
  const quickActions = document.getElementById("chatbotQuickActions");
  const typing = document.getElementById("chatbotTyping");
  const welcomeMessage = "Hi, ask for wedding, party, office, college, or colour-based outfit ideas and I will show clickable product picks from your website.";

  if (!launcher || !panel || !form || !input || !messages || !clearButton || !quickActions || !typing) return;

  const setChatbotOpen = (isOpen) => {
    panel.hidden = !isOpen;
    panel.setAttribute("aria-hidden", String(!isOpen));
    launcher.setAttribute("aria-expanded", String(isOpen));
    launcher.textContent = isOpen ? "Close Help" : "Style Help";
    if (isOpen) {
      window.setTimeout(() => input.focus(), 40);
    }
  };

  const appendChatMessage = (role, text, options = {}) => {
    const article = document.createElement("article");
    article.className = `chatbot-message chatbot-message-${role}`;
    if (role === "assistant" && options.products?.length) {
      article.classList.add("chatbot-message-has-products");
    }

    const messageParts = [`<p>${escapeHtml(text)}</p>`];
    if (role === "assistant" && options.products?.length) {
      messageParts.push(`
        <div class="chatbot-product-list">
          ${options.products.map((product) => createChatbotProductCardMarkup(product)).join("")}
        </div>
      `);
    }

    article.innerHTML = messageParts.join("");
    messages.appendChild(article);
    messages.scrollTop = messages.scrollHeight;
  };

  const resetChatbot = () => {
    messages.innerHTML = "";
    appendChatMessage("assistant", welcomeMessage);
    typing.hidden = true;
    input.value = "";
  };

  const sendChatMessage = (text) => {
    const cleanText = text.trim();
    if (!cleanText) return;

    appendChatMessage("user", cleanText);
    input.value = "";
    typing.hidden = false;
    messages.scrollTop = messages.scrollHeight;

    window.setTimeout(() => {
      typing.hidden = true;
      const response = buildChatbotResponse(cleanText);
      appendChatMessage("assistant", response.text, { products: response.products });
    }, 320);
  };

  launcher.addEventListener("click", () => {
    setChatbotOpen(panel.hidden);
  });

  clearButton.addEventListener("click", resetChatbot);

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    sendChatMessage(input.value);
  });

  quickActions.addEventListener("click", (event) => {
    const action = event.target.closest("[data-prompt]");
    if (!action) return;
    if (panel.hidden) setChatbotOpen(true);
    sendChatMessage(action.dataset.prompt || "");
  });

  document.addEventListener("click", (event) => {
    if (panel.hidden) return;
    if (panel.contains(event.target) || launcher.contains(event.target)) return;
    setChatbotOpen(false);
  });

  document.addEventListener("keydown", (event) => {
    if (event.key !== "Escape" || panel.hidden) return;
    setChatbotOpen(false);
    launcher.focus();
  });

  setChatbotOpen(false);
  resetChatbot();
}

const CHATBOT_RULES = [
  {
    pattern: /(college|campus|class)/,
    reply: "For college wear, keep it simple: easy tops, denims, co-ords, or light kurtis.",
  },
  {
    pattern: /(party|evening|night out)/,
    reply: "For party wear, fitted dresses, statement tops, or clean co-ord sets are a good start.",
  },
  {
    pattern: /(office|work|formal)/,
    reply: "For office outfits, try structured tops, trousers, blazers, or refined kurtis in cleaner colours.",
  },
  {
    pattern: /(wedding|bridal|ceremony)/,
    reply: "For wedding looks, sarees, ethnic sets, and embellished festive pieces fit best in this project.",
  },
  {
    pattern: /(teen|teenage|young girl|college girl)/,
    reply: "For teenage girls, casual tops, easy dresses, and lighter separates usually feel most natural.",
  },
  {
    pattern: /(married women|married|family occasion)/,
    reply: "For married women, festive kurtis, sarees, and ethnic sets often appear as stronger matches.",
  },
  {
    pattern: /(soft neutrals|neutral|beige|cream|nude)/,
    reply: "Soft neutrals work well when you want a calm look with beige, cream, off-white, or nude tones.",
  },
  {
    pattern: /(bold colours|bold|bright|vibrant|red|pink)/,
    reply: "Bold colours are useful when you want more energy, especially for party or festive looks.",
  },
  {
    pattern: /(festive|ethnic|traditional)/,
    reply: "For festive styles, embroidered kurtis, ethnic sets, and traditional wear are a safe direction.",
  },
];

function getChatbotReply(message) {
  const text = String(message || "").toLowerCase();
  const matchedRule = CHATBOT_RULES.find((rule) => rule.pattern.test(text));

  if (/(hello|hi|hey)/.test(text)) {
    return "Hi, tell me the occasion or colour direction and I will suggest a simple starting point.";
  }

  if (matchedRule) {
    return `${matchedRule.reply} You can also compare it with the Women page trend finder.`;
  }

  return "Try asking about college wear, office outfits, wedding styles, soft neutrals, or bold colours.";
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
        <a class="button button-primary" href="./women.html#shop">Start Shopping</a>
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
        <a class="button button-secondary" href="./women.html#shop">Go Back To Shop</a>
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
