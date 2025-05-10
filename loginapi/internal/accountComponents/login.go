package accountComponents

import (
	"log"
	"fmt"
	"time"
	"context"
	"net/http"
	"encoding/json"
	"golang.org/x/crypto/bcrypt"
	"github.com/Vchen7629/Cyphria/loginapi/internal/components"
	dbconn "github.com/Vchen7629/Cyphria/loginapi/config/postgres"
)

type LoginCredentials struct {
	Username string `json:"username"`
	Password string `json:"password"`
}

func AuthenticateUser(username, password string) (bool, string) {
	var storedpasswordhash string;
	var storeduuid string;

	err := dbconn.DBConn.QueryRow(context.Background(), 
		"SELECT password, uuid FROM useraccount WHERE username = $1",
	username).Scan(&storedpasswordhash, &storeduuid)

	if err != nil {
		log.Println("Invalid username or password")
		return false, ""
	}

	bcryptErr := bcrypt.CompareHashAndPassword([]byte(storedpasswordhash), []byte(password))

	if bcryptErr != nil {
		log.Println("Invalid password from comparing hashes")
		return false, ""
	}

	return true, storeduuid
}

func SessionHandler(username string, uuid string) (error, string, bool){
	tokenString, err, sessionSuccess := components.GenerateSessionToken()

	if err != nil {
		return fmt.Errorf("Error Generating Session Token"), "", false
	}

	redisErr := components.UpdateRedisSessionID(tokenString, username, uuid)

	if redisErr != nil {
		return fmt.Errorf("error updating redis session id"), "", false
	} else if !sessionSuccess {
		return fmt.Errorf("error generating session id"), "", false
	}
	
	return nil, tokenString, true
}

func LoginHandler(w http.ResponseWriter, r *http.Request) {
	start := time.Now()
	var payload LoginCredentials
	w.Header().Set("Content-Type", "application/json")

	requestbodyerr := json.NewDecoder(r.Body).Decode(&payload)
	parsetime := time.Since(start)
	if requestbodyerr != nil {
		http.Error(w, "error parsing json body", http.StatusBadRequest)
		return
	}

	authStart := time.Now()
	login, uuid := AuthenticateUser(payload.Username, payload.Password)
	authTime := time.Since(authStart)

	if !login {
		w.WriteHeader(http.StatusUnauthorized)
		json.NewEncoder(w).Encode(map[string]string{
			"message": "Invalid username or password",
		})
		return
	}

	jwtStart := time.Now()
	err, tokenString, sessionSuccess := SessionHandler(payload.Username, uuid)
	jwtSince := time.Since(jwtStart)

	if !sessionSuccess && err != nil {
		w.WriteHeader(http.StatusInternalServerError)
		json.NewEncoder(w).Encode(map[string]string{
			"message": err.Error(),
		})
		return
	}
	
	cookie := http.Cookie{
		Name: 		"accessToken",
		Value: 		tokenString,
		Expires: 	time.Now().Add(24 * time.Hour),
		Path: 		"/",
		Secure:     true,
		HttpOnly:   true,
		SameSite:   http.SameSiteLaxMode,
	}

	http.SetCookie(w, &cookie)

	respStart := time.Now()
	response := map[string]string{
		"message": "Login Successful!",
		"username": payload.Username,
	}
	respTime := time.Since(respStart)

	totalTime := time.Since(start)
	json.NewEncoder(w).Encode(response)
	log.Printf("Login timing - Parse: %v, Auth: %v, JWT: %v, Response: %v, Total: %v",
		parsetime, authTime, jwtSince, respTime, totalTime)
}