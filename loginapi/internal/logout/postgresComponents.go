package logout

import (
	"context"
	"fmt"
	dbconn "github.com/Vchen7629/Cyphria/loginapi/config/postgres"
)

func RemoveSessionTokenPostgres(uuid string) error {
	if uuid == "" {
		return fmt.Errorf("No uuid provided")
	}

	result, updateErr := dbconn.DBConn.Exec(context.Background(), `
		UPDATE useraccount
		SET sessionid = NULL
		WHERE uuid = $1
	`, uuid)

	if updateErr != nil {
		return fmt.Errorf("Internal Error")
	}

	if result.RowsAffected() == 0 {
		return fmt.Errorf("No rows were updated")
	}

	return nil
}

func PostgresHandler(UUID string) (bool, error) {
	err := RemoveSessionTokenPostgres(UUID)

	if err != nil {
		return false, err
	}

	return true, nil
}