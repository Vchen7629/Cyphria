package accountComponents

import (
	"log"
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

type LoginResponse struct {
	Token string `json:"token"`
	Message string `json:"message"`
}

type UserInfo struct {
	UserId string
	Username string
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

func SessionHandler(w http.ResponseWriter, username string, uuid string) {
	tokenString, err := components.GenerateSessionToken()

	if err != nil {
		w.Header().Set("content-type", "application/json")
		w.WriteHeader(http.StatusInternalServerError)
		json.NewEncoder(w).Encode(map[string]string{
			"message": "Error Generating Session Token",
		})
	}

	redisErr := components.UpdateRedisSessionID(tokenString, username, uuid)

	if redisErr != nil {
		w.Header().Set("content-type", "application/json")
		w.WriteHeader(http.StatusInternalServerError)
		json.NewEncoder(w).Encode(map[string]string{
			"message": "error updating redis session id",
		})
	}

	sessionErr := components.SaveSessionTokenPostgres(username, tokenString)

	if sessionErr != nil && sessionErr.Error() == "Error updating sessionID for username" {
		w.Header().Set("content-type", "application/json")
		w.WriteHeader(http.StatusInternalServerError)
		json.NewEncoder(w).Encode(map[string]string{
			"message": sessionErr.Error(),
		})
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

}

func LoginHandler(w http.ResponseWriter, r *http.Request) {
	start := time.Now()
	var payload LoginCredentials

	requestbodyerr := json.NewDecoder(r.Body).Decode(&payload)
	parsetime := time.Since(start)
	if requestbodyerr != nil {
		http.Error(w, "error parsing json body", http.StatusBadRequest)
		return
	}

	authStart := time.Now()
	login, uuid := AuthenticateUser(payload.Username, payload.Password)
	authTime := time.Since(authStart)

	//jwtStart := time.Now()
	//SessionHandler(w, payload.Username, uuid)
	//jwtSince := time.Since(jwtStart)

	if !login {
		w.Header().Set("Content-Type","application/json")
		w.WriteHeader(http.StatusUnauthorized)
		json.NewEncoder(w).Encode(map[string]string{
			"message": "Invalid username or password",
		})
	} else {
		w.Header().Set("Content-Type", "application/json")

		respStart := time.Now()
		response := map[string]interface{}{
			"message": "Login Successful!",
			"user": map[string]string{
				"username": payload.Username,
				"uuid": uuid,
			},
		}
		respTime := time.Since(respStart)

		totalTime := time.Since(start)
		json.NewEncoder(w).Encode(response)
		log.Printf("Login timing - Parse: %v, Auth: %v, JWT: %v, Response: %v, Total: %v",
			parsetime, authTime, /*jwtSince,*/ respTime, totalTime)
	}
}