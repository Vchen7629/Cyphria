package login

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"time"

	"github.com/golang-jwt/jwt"
	dbconn "github.com/vchen7629/cyphria/login-api/internal/db_connection"
	"golang.org/x/crypto/bcrypt"
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

type Claims struct {
	*jwt.StandardClaims
	TokenType string
	UserInfo
}

func AuthenticateUser(username, password string) (bool, string, error) {
	var storedpasswordhash string;
	var storeduuid string;

	err := dbconn.DBConn.QueryRow(context.Background(), 
		"SELECT password, uuid FROM useraccount WHERE username = $1",
	username).Scan(&storedpasswordhash, &storeduuid)

	if err != nil {
		return false, "", fmt.Errorf("error querying database: %w", err)
	}

	err = bcrypt.CompareHashAndPassword([]byte(storedpasswordhash), []byte(password))
	if err != nil {
		return false, "", nil
	}

	return true, storeduuid, nil
}

func GenerateJwtToken(w http.ResponseWriter, username string, uuid string)  {
	claims := &Claims{
		UserInfo: UserInfo{
			Username: 	username,
			UserId: 	uuid,
		},
		StandardClaims: &jwt.StandardClaims{
			ExpiresAt: 	time.Now().Add(24 * time.Hour).Unix(),
			Issuer: 	"Cyphria",
		},
	}

	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)

	tokenString, err := token.SignedString([]byte("AllYourBase"))
    if err != nil {
        http.Error(w, "Failed to generate token", http.StatusInternalServerError)
        return
    }

	cookie := http.Cookie{
		Name: "Cookie",
		Value: tokenString,
		Expires: time.Now().Add(24 * time.Hour),
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
	defer r.Body.Close()

	authStart := time.Now()
	login, uuid, err := AuthenticateUser(payload.Username, payload.Password)
	authTime := time.Since(authStart)

	if err != nil {
		log.Printf("Authentication error: %v", err)
		http.Error(w, "Something went wrong", http.StatusInternalServerError)
		return
	}

	if !login {
		w.Header().Set("Content-Type","application/json")
		w.WriteHeader(http.StatusNotFound)
		json.NewEncoder(w).Encode(map[string]string{
			"message": "username or password doesn't match",
		})
	}

	fmt.Print(uuid)
	jwtStart := time.Now()
	//GenerateJwtToken(w, payload.Username, uuid)
	jwtSince := time.Since(jwtStart)
	w.Header().Set("Content-Type", "application/json")

	respStart := time.Now()
	response := map[string]string{
		"message": "Login Successful!",
		/*"user": map[string]string{
            "username": payload.Username,
            "uuid": uuid,
        },*/
	}
	respTime := time.Since(respStart)

	totalTime := time.Since(start)
	json.NewEncoder(w).Encode(response)
	log.Printf("Login timing - Parse: %v, Auth: %v, JWT: %v, Response: %v, Total: %v",
        parsetime, authTime, jwtSince, respTime, totalTime)
}