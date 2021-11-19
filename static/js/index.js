const updateOrderListener = (e) => {
  const target = e.target;
  const productID = target.dataset.product;
  const action = target.dataset.action;

  // CUSTOM COOKIE APPROACH
  // if (isAnonymous) updateCartCookie(productID, action);
  // else updateUserOrder(productID, action);
  updateUserOrder(productID, action);
};

function addUpdateCartEvent() {
  console.log("update cart event listener");
  $(".update-cart").on("click", updateOrderListener);
}

function refreshUIcomponents() {
  // reload cart elements to be updated
  $(".cart-total-wrapper").load(location.href + " #cart-total");
  $(".cart-content-wrapper").load(
    location.href + " .cart-content-wrapper > *",
    addUpdateCartEvent
  );
}
const updateUserOrder = async (productID, action) => {
  console.log("sending data....");
  url = "/update-item/";
  const res = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrftoken,
    },
    body: JSON.stringify({ productId: productID, action: action }),
  });

  if (res.ok) {
    refreshUIcomponents();
  } else {
    throw new Error("HTTP status " + res.status);
  }
};

$(".update-cart").on("click", updateOrderListener);

// CUSTOM cart cookie approach
// const updateCartCookie = (productID, action) => {
//   console.log("ok Guest cart update");

//   if (action === "add") {
//     let found = false;
//     cart.items.map((item) => {
//       if (item.id === productID) {
//         found = true;
//         return { ...item, quantity: item.quantity++ };
//       }
//       return item;
//     });
//     if (!found) cart.items = [...cart.items, { id: productID, quantity: 1 }];

//     cart.num_items += 1;
//   } else {
//     let last = false;
//     cart.items.map((item) => {
//       if (item.id === productID) {
//         if (item.quantity <= 1) last = true;
//         return { ...item, quantity: item.quantity-- };
//       }
//       return item;
//     });
//     if (last) cart.items = cart.items.filter((item) => item.id !== productID);

//     cart.num_items -= 1;
//   }
//   document.cookie = "cart=" + JSON.stringify(cart) + ";domain=;path=/";

//   refreshUIcomponents();
// };
