package login

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"time"
	"errors"
	"database/sql"
	dbconn "github.com/Vchen7629/Cyphria/loginapi/config/postgres"
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

func AuthenticateUser(username, password string) (bool, string, error) {
	var storedpasswordhash string;
	var storeduuid string;

	err := dbconn.DBConn.QueryRow(context.Background(), 
		"SELECT password, uuid FROM useraccount WHERE username = $1",
	username).Scan(&storedpasswordhash, &storeduuid)

	if err != nil {
		return false, "", fmt.Errorf("Invalid username or password")
	}

	err = bcrypt.CompareHashAndPassword([]byte(storedpasswordhash), []byte(password))
	if err != nil {
		return false, "", fmt.Errorf("Invalid username or password")
	}

	return true, storeduuid, nil
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
	login, uuid, err := AuthenticateUser(payload.Username, payload.Password)
	authTime := time.Since(authStart)

	if err != nil && errors.Is(err, sql.ErrNoRows) {
		w.Header().Set("Content-Type","application/json")
		w.WriteHeader(http.StatusNotFound)
		json.NewEncoder(w).Encode(map[string]string{
			"message": "Invalid username or password",
		})
	} else if err != nil {
		w.Header().Set("Content-Type","application/json")
		w.WriteHeader(http.StatusNotFound)
		json.NewEncoder(w).Encode(map[string]string{
			"message": "Invalid username or password",
		})
	}

	if !login {
		w.Header().Set("Content-Type","application/json")
		w.WriteHeader(http.StatusUnauthorized)
		json.NewEncoder(w).Encode(map[string]string{
			"message": "Invalid username or password",
		})
	}

	fmt.Print(uuid)
	jwtStart := time.Now()
	SessionHandler(w, payload.Username, uuid)
	jwtSince := time.Since(jwtStart)
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
        parsetime, authTime, jwtSince, respTime, totalTime)
}