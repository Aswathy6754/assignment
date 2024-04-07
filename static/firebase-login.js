// Import the functions you need from the SDKs you need
import { initializeApp } from "https://www.gstatic.com/firebasejs/10.10.0/firebase-app.js";
// import { getAnalytics } from "https://www.gstatic.com/firebasejs/10.10.0/firebase-analytics.js";
import { getAuth, signInWithEmailAndPassword, createUserWithEmailAndPassword,signOut } from "https://www.gstatic.com/firebasejs/10.10.0/firebase-auth.js";


// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
  apiKey: "AIzaSyCO958GOx-_bYP-zXH-k4kQHPUaU_coCYo",
  authDomain: "assignment-c4726.firebaseapp.com",
  projectId: "assignment-c4726",
  storageBucket: "assignment-c4726.appspot.com",
  messagingSenderId: "759842651592",
  appId: "1:759842651592:web:7921ea83db935bf166d4fd",
  measurementId: "G-0ZKLB2S4JJ"
};







window.addEventListener('load', function () {

  const app = initializeApp(firebaseConfig);
  const auth = getAuth(app)
  // updateUI(document.cookie)

  let signUpButton = document.getElementById('sign-up')

  if (signUpButton) {
    document.getElementById('sign-up').addEventListener('click', () => {
      const email = document.getElementById('email').value
      const password = document.getElementById('password').value
      let errorMessage = document.getElementById('error-message')
      let successMessage = document.getElementById('success-message')


      console.log(email, password)
      createUserWithEmailAndPassword(auth, email, password)
        .then((userCredential) => {
          const user = userCredential.user;
          const email = user.email
          const uid = user.uid
          user.getIdToken().then((token) => {
            errorMessage.innerText= ""
            successMessage.innerText ='Successfully Signup'

            document.cookie = "token=" + token + ';path=/;Samesite=Strict';
            document.cookie = "email=" + email + ';path=/;Samesite=Strict';
            document.cookie = "uid=" + uid + ';path=/;Samesite=Strict';
            window.location = '/'
          })
        })
        .catch((error) => {
          console.log(error.code + error.message)
          errorMessage.innerText= error.message
          successMessage.innerText =""

        })
    })
  } 


  let loginButton = document.getElementById('login')

  if (loginButton) {
    document.getElementById('login').addEventListener('click', () => {
      const email = document.getElementById('email').value
      const password = document.getElementById('password').value
      let errorMessage = document.getElementById('error-message')
      let successMessage = document.getElementById('success-message')

      signInWithEmailAndPassword(auth, email, password)
        .then((userCredential) => {
          const user = userCredential.user;
          const email = user.email
          const uid = user.uid

          user.getIdToken().then((token) => {
            errorMessage.innerText= ""
            successMessage.innerText ='Successfully Logged-in'

            document.cookie = "token=" + token + ';path=/;Samesite=Strict';
            document.cookie = "email=" + email + ';path=/;Samesite=Strict';
            document.cookie = "uid=" + uid + ';path=/;Samesite=Strict';

            window.location = '/'
          })
        })
        .catch((error) => {
          console.log(error.code + error.message)
          errorMessage.innerText= error.message
          successMessage.innerText =""

        })
    })
  }


  let signOutButton = document.getElementById('sign-out')
  if (signOutButton) {

    document.getElementById('sign-out').addEventListener('click', () => {
      document.cookie = 'token' + "=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
      document.cookie = 'email' + "=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
      document.cookie = "uid" + "=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
      window.location='/'
      signOut(auth).then(( res) => {
      }).catch(()=>{
      })

      const apiUrl = `http://127.0.0.1:8000/logout`;
      const requestOptions = {
        method: "GET",
        headers: {
          "Content-Type": "application/json"
        },
      };

      fetch(apiUrl, requestOptions)
        .then(response => {
          if (!response.ok) {
            throw new Error("Failed Logout");
          }
        })
        .catch(error => {
          console.error("Error logout:", error);
        });

    })
  }

})



function parseCookieToken(token) {
  var strings = token.split(';')

  for (let i = 0; i < strings.length; i++) {
    var temp = strings[i].split('=')
    if (temp[0] == "token")
      return temp[1]
  }
  return ""
}