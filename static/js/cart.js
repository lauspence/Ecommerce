// cart.js

document.addEventListener('DOMContentLoaded', function () {
    // Function to log selected options to console and update size in the database
    function logSelectedOptions() {
        var sizeSelects = document.querySelectorAll('.size-select');

        sizeSelects.forEach(function (select) {
            var productId = select.getAttribute('data-product');
            var selectedOption = select.options[select.selectedIndex].text;

            console.log('Product ID:', productId, 'Selected Size:', selectedOption);

            if (user != 'AnonymousUser') {
                // If the user is logged in, update the size in the database
                updateSizeInDatabase(productId, selectedOption);
            }
        });
    }

    // Attach event listener to the size selects for logging and updating size
    var sizeSelects = document.querySelectorAll('.size-select');
    sizeSelects.forEach(function (select) {
        select.addEventListener('change', logSelectedOptions);

        // Retrieve the selected size from cookies and set it on page load
        var productId = select.getAttribute('data-product');
        var selectedSize = getSelectedSizeFromCookies(productId);
        if (selectedSize) {
            select.value = selectedSize;
        }
    });

    // Your existing update-cart script
    var updateBtns = document.getElementsByClassName('update-cart');

    for (var i = 0; i < updateBtns.length; i++) {
        updateBtns[i].addEventListener('click', function () {
            var productId = this.dataset.product;
            var action = this.dataset.action;

            console.log('productId:', productId, 'action:', action);
            console.log('USER:', user);

            if (user == 'AnonymousUser') {
                addCookieItem(productId, action);
            } else {
                updateUserOrder(productId, action);
            }
        });
    }

    function addCookieItem(productId, action) {
        console.log('Not logged in...');

        if (action == 'add') {
            if (cart[productId] == undefined) {
                cart[productId] = { 'quantity': 1 };
            } else {
                cart[productId]['quantity'] += 1;
            }
        }

        if (action == 'remove') {
            cart[productId]['quantity'] -= 1;

            if (cart[productId]['quantity'] <= 0) {
                console.log('Remove Item');
                delete cart[productId];
            }
        }
        console.log('Cart:', cart);
        document.cookie = 'cart=' + JSON.stringify(cart) + ";domain=;path=/";
        // location.reload()
    }

    function updateUserOrder(productId, action) {
        console.log('User is logged in, sending data...');

        var url = '/update_item/';

        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken,
            },
            body: JSON.stringify({ 'productId': productId, 'action': action })
        })
            .then((response) => {
                return response.json();
            })
            .then((data) => {
                console.log('data:', data);
                location.reload();
            });
    }

    // Function to update the selected size in the database
// Function to update the selected size in the database
function updateSizeInDatabase(productId, selectedSize) {
    var url = '/update_size/';

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': csrftoken,
        },
        body: new URLSearchParams({
            'productId': productId,
            'selectedSize': selectedSize,
        }),
    })
        .then((response) => {
            return response.json();
        })
        .then((data) => {
            console.log('Size updated in the database:', data);
        });
}

    // Function to retrieve the selected size from cookies
    function getSelectedSizeFromCookies(productId) {
        if (document.cookie && document.cookie.indexOf('cart=') !== -1) {
            var cartData = JSON.parse(document.cookie.split('cart=')[1].split(';')[0]);
            if (cartData[productId] && cartData[productId]['size']) {
                return cartData[productId]['size'];
            }
        }
        return null;
    }
});
