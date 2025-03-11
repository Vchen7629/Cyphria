package signup

import (
	"context"
	"encoding/json"
	"log"
	"net/http"

	dbconn "github.com/vchen7629/cyphria/login-api/internal/db_connection"
)

type SignUpUserInfo struct {
	Username string `json:"username"`
	Email string `json:"email"`
	Password string `json:"password"`
}

func CreateNewUser() error {
	_, err := dbconn.DBConn.Exec(context.Background(), `
		INSERT INTO useraccount (uuid, username, password, creation)
		VALUES (
			'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a26',
			'tribbie',
			'sunday',
			'2025-03-10 19:58:39'
		) 
		ON CONFLICT (username)
		DO NOTHING;
	`)

	if err != nil {
		log.Fatalf("Error creating a new user: %v", err)
	}
	
	return nil
}

func HttpHandler(w http.ResponseWriter, r *http.Request) {
	if err := CreateNewUser(); err != nil {
		http.Error(w, "Error Creating User", http.StatusInternalServerError)
		return
	}

	response := map[string]string{
		"message": "user created Successfully!",
	}

	w.Header().Set("Content-Type","application/json")
	w.WriteHeader(http.StatusCreated)
	json.NewEncoder(w).Encode(response)
}