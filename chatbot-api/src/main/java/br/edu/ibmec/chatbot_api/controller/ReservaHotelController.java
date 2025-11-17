package br.edu.ibmec.chatbot_api.controller;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.*;

@RestController
public class ReservaHotelController {

    private final List<Map<String, Object>> reservasHotel = new ArrayList<>();

    @PostMapping("/reservas-hotel")
    public ResponseEntity<Void> criarReservaHotel(@RequestBody Map<String, Object> reserva) {

        System.out.println("Reserva de hotel recebida: " + reserva);
        reservasHotel.add(reserva);

        return ResponseEntity.status(HttpStatus.CREATED).build();
    }

    @GetMapping("/reservas-hotel")
    public ResponseEntity<?> consultarReservasHotel(@RequestParam String cpf) {

        List<Map<String, Object>> resultado = reservasHotel.stream()
                .filter(r -> ((Map<String,Object>)r.get("cliente")).get("cpf").equals(cpf))
                .toList();

        if (resultado.isEmpty()) {
            return ResponseEntity.ok(Collections.emptyList());
        }

        return ResponseEntity.ok(resultado);
    }
}
