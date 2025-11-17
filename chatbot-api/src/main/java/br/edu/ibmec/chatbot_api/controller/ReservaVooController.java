package br.edu.ibmec.chatbot_api.controller;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.*;

@RestController
public class ReservaVooController {

    private final List<Map<String, Object>> reservasVoo = new ArrayList<>();

    @PostMapping("/reservas-voo")
    public ResponseEntity<Void> criarReservaVoo(@RequestBody Map<String, Object> reserva) {

        System.out.println("Reserva de voo recebida: " + reserva);
        reservasVoo.add(reserva);

        return ResponseEntity.status(HttpStatus.CREATED).build();
    }

    @GetMapping("/reservas-voo")
    public ResponseEntity<?> consultarReservasVoo(@RequestParam String cpf) {

        List<Map<String, Object>> resultado = reservasVoo.stream()
                .filter(r -> ((Map<String,Object>)r.get("cliente")).get("cpf").equals(cpf))
                .toList();

        if (resultado.isEmpty()) {
            return ResponseEntity.ok(Collections.emptyList());
        }

        return ResponseEntity.ok(resultado);
    }
}
