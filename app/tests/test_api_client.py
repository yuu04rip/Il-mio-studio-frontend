import os
import sys
from unittest.mock import patch, MagicMock

import pytest

# aggiungi la root del progetto al PYTHONPATH
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from app.api import api as api_module
from app.api.api import APIClient

@pytest.fixture
def client():
    c = APIClient()
    c.set_token("test-token")
    return c


def _mock_response(status_code=200, json_data=None, content=None):
    mock_resp = MagicMock()
    mock_resp.status_code = status_code
    mock_resp.json.return_value = json_data
    mock_resp.content = content
    # raise_for_status non deve fare nulla se 2xx
    mock_resp.raise_for_status.return_value = None
    return mock_resp


# --- helper headers ----------------------------------------------------------

def test_headers_with_token():
    c = APIClient()
    c.set_token("abc123")
    assert c._headers() == {"Authorization": "Bearer abc123"}


def test_headers_without_token():
    c = APIClient()
    assert c._headers() == {}


# --- AUTH --------------------------------------------------------------------

@patch("app.api.api.requests.post")
def test_login_success(mock_post, client):
    resp_data = {"access_token": "token123", "token_type": "bearer"}
    mock_post.return_value = _mock_response(json_data=resp_data)

    data = client.login("user@example.com", "pwd")

    assert data == resp_data
    assert client.token == "token123"
    mock_post.assert_called_once_with(
        f"{api_module.API_BASE}/auth/login",
        json={"email": "user@example.com", "password": "pwd"},
    )


@patch("app.api.api.requests.post")
def test_register_success(mock_post, client):
    resp_data = {"access_token": "tokenXYZ", "user_id": 1}
    mock_post.return_value = _mock_response(json_data=resp_data)

    user_data = {"email": "new@example.com", "password": "pwd"}
    data = client.register(user_data)

    assert data == resp_data
    assert client.token == "tokenXYZ"
    mock_post.assert_called_once_with(
        f"{api_module.API_BASE}/auth/register",
        json=user_data,
    )


@patch("app.api.api.requests.get")
def test_get_me(mock_get, client):
    resp_data = {"id": 1, "email": "user@example.com"}
    mock_get.return_value = _mock_response(json_data=resp_data)

    data = client.get_me()

    assert data == resp_data
    mock_get.assert_called_once_with(
        f"{api_module.API_BASE}/users/me",
        headers={"Authorization": "Bearer test-token"},
    )


# --- DIPENDENTE / NOTAIO ----------------------------------------------------

@patch("app.api.api.requests.post")
def test_register_dipendente(mock_post, client):
    resp_data = {"access_token": "dip-token", "id": 10}
    mock_post.return_value = _mock_response(json_data=resp_data)

    payload = {"email": "dip@example.com", "password": "pwd"}
    data = client.register_dipendente(payload)

    assert data == resp_data
    assert client.token == "dip-token"
    mock_post.assert_called_once_with(
        f"{api_module.API_BASE}/auth/register-dipendente",
        json=payload,
    )


@patch("app.api.api.requests.post")
def test_add_dipendente(mock_post, client):
    resp_data = {"id": 5, "tipo": "DIPENDENTE"}
    mock_post.return_value = _mock_response(json_data=resp_data)

    user_data = {"email": "d@example.com", "password": "pwd"}
    data = client.add_dipendente(user_data, "DIPENDENTE")

    assert data == resp_data
    # user_data non deve essere mutato
    assert "tipo" not in user_data
    mock_post.assert_called_once()
    called_url = mock_post.call_args[0][0]
    called_json = mock_post.call_args[1]["json"]
    called_headers = mock_post.call_args[1]["headers"]

    assert called_url == f"{api_module.API_BASE}/studio/dipendenti"
    assert called_json["email"] == "d@example.com"
    assert called_json["tipo"] == "DIPENDENTE"
    assert called_headers == {"Authorization": "Bearer test-token"}


@patch("app.api.api.requests.post")
def test_add_notaio(mock_post, client):
    resp_data = {"id": 7, "ruolo": "NOTAIO"}
    mock_post.return_value = _mock_response(json_data=resp_data)

    user_data = {"email": "n@example.com", "password": "pwd"}
    data = client.add_notaio(user_data, "ABC123")

    assert data == resp_data
    mock_post.assert_called_once_with(
        f"{api_module.API_BASE}/auth/register-notaio",
        json={"email": "n@example.com", "password": "pwd", "codice_notarile": "ABC123"},
        headers={"Authorization": "Bearer test-token"},
    )

@patch("app.api.api.requests.delete")
def test_elimina_dipendente(mock_delete, client):
    resp_data = {"msg": "ok"}
    mock_delete.return_value = _mock_response(json_data=resp_data)

    data = client.elimina_dipendente(10)

    assert data == resp_data
    mock_delete.assert_called_once_with(
        f"{api_module.API_BASE}/studio/dipendente/10",
        headers={"Authorization": "Bearer test-token"},
    )


# --- SERVIZI / BACKUP -------------------------------------------------------

@patch("app.api.api.requests.post")
def test_archivia_servizio(mock_post, client):
    resp_data = {"id": 1, "archived": True}
    mock_post.return_value = _mock_response(json_data=resp_data)

    data = client.archivia_servizio(1)

    assert data == resp_data
    mock_post.assert_called_once_with(
        f"{api_module.API_BASE}/studio/servizi/1/archivia",
        headers={"Authorization": "Bearer test-token"},
    )


@patch("app.api.api.requests.put")
def test_dearchivia_servizio(mock_put, client):
    resp_data = {"id": 1, "archived": False}
    mock_put.return_value = _mock_response(json_data=resp_data)

    data = client.dearchivia_servizio(1)

    assert data == resp_data
    mock_put.assert_called_once_with(
        f"{api_module.API_BASE}/backup/backup/dearchivia-servizio/1",
        headers={"Authorization": "Bearer test-token"},
    )


@patch("app.api.api.requests.put")
def test_modifica_servizio_archiviato(mock_put, client):
    resp_data = {"id": 1, "archived": True}
    mock_put.return_value = _mock_response(json_data=resp_data)

    data = client.modifica_servizio_archiviato(1, True)

    assert data == resp_data
    mock_put.assert_called_once_with(
        f"{api_module.API_BASE}/backup/backup/servizi/1/modifica-archiviazione",
        json={"statoServizio": True},
        headers={"Authorization": "Bearer test-token"},
    )


@patch("app.api.api.requests.post")
def test_crea_servizio_con_codice_e_dipendente(mock_post, client):
    resp_data = {"id": 3, "codiceServizio": "SERV-000003"}
    mock_post.return_value = _mock_response(json_data=resp_data)

    data = client.crea_servizio(cliente_id=1, tipo="ATTO", codice_corrente=5, dipendente_id=2)

    assert data == resp_data
    mock_post.assert_called_once_with(
        f"{api_module.API_BASE}/studio/servizi",
        json={"cliente_id": 1, "tipo": "ATTO", "codiceCorrente": 5, "dipendente_id": 2},
        headers={"Authorization": "Bearer test-token"},
    )


@patch("app.api.api.requests.post")
def test_crea_servizio_senza_codice(mock_post, client):
    resp_data = {"id": 4, "codiceServizio": "SERV-000004"}
    mock_post.return_value = _mock_response(json_data=resp_data)

    data = client.crea_servizio(cliente_id=1, tipo="ATTO")

    assert data == resp_data
    mock_post.assert_called_once_with(
        f"{api_module.API_BASE}/studio/servizi",
        json={"cliente_id": 1, "tipo": "ATTO"},
        headers={"Authorization": "Bearer test-token"},
    )


# --- DOCUMENTAZIONE SERVIZIO / CLIENTE --------------------------------------

@patch("app.api.api.requests.get")
def test_visualizza_documentazione_servizio(mock_get, client):
    resp_data = [{"id": 1}, {"id": 2}]
    mock_get.return_value = _mock_response(json_data=resp_data)

    data = client.visualizza_documentazione_servizio(10)

    assert data == resp_data
    mock_get.assert_called_once_with(
        f"{api_module.API_BASE}/documentazione/servizi/10/documenti",
        headers={"Authorization": "Bearer test-token"},
    )


@patch("app.api.api.requests.get")
def test_visualizza_documentazione_cliente(mock_get, client):
    resp_data = [{"id": 1}]
    mock_get.return_value = _mock_response(json_data=resp_data)

    data = client.visualizza_documentazione_cliente(5)

    assert data == resp_data
    mock_get.assert_called_once_with(
        f"{api_module.API_BASE}/documentazione/documenti/visualizza/5",
        headers={"Authorization": "Bearer test-token"},
    )


@patch("app.api.api.requests.get")
def test_download_documentazione(mock_get, client):
    content = b"file-bytes"
    mock_get.return_value = _mock_response(content=content)

    data = client.download_documentazione(123)

    assert data == content
    mock_get.assert_called_once_with(
        f"{api_module.API_BASE}/documentazione/download/123",
        headers={"Authorization": "Bearer test-token"},
        stream=True,
    )


# --- SMOKE TEST IMPORT MAIN -------------------------------------------------

def test_import_main():
    # verifica solo che main.py si importi senza errori
    import main  # noqa: F401

