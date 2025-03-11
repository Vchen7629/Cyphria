package signup

import (
	"context"
	"encoding/json"
	"fmt"
	"net/http"

	"github.com/jackc/pgx/v5"
	dbconn "github.com/vchen7629/cyphria/login-api/internal/db_connection"
)

type SignUpUserInfo struct {
	Username string `json:"username"`
	Email string `json:"email"`
	Password string `json:"password"`
}

func CreateNewUser() (bool, error) {
	var inserted bool
	err := dbconn.DBConn.QueryRow(context.Background(), `
		INSERT INTO useraccount (uuid, username, password, creation)
		VALUES (
			'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a49',
			'castorice',
			'sunday',
			'2025-03-10 19:58:39'
		) 
		ON CONFLICT (username) DO NOTHING
		RETURNING true;
	`).Scan(&inserted)

	if err == pgx.ErrNoRows {
		return false, nil
	}

	if err != nil {
		return false, fmt.Errorf("error creating a new user: %w", err)
	}
	
	return true, nil
}

func HttpHandler(w http.ResponseWriter, r *http.Request) {
	created, err := CreateNewUser()

	if err != nil {
		http.Error(w, fmt.Sprintf("Error creating user: %v", err), http.StatusInternalServerError)
		return
	}

	if !created {
		w.Header().Set("Content-Type","application/json")
		w.WriteHeader(http.StatusConflict)
		json.NewEncoder(w).Encode(map[string]string{
			"message": "username or uuid already exists",
		})
		return
	}

	response := map[string]string{
		"message": "user created Successfully!",
	}

	w.Header().Set("Content-Type","application/json")
	w.WriteHeader(http.StatusCreated)
	json.NewEncoder(w).Encode(response)
}