// A simple 4-bit synchronous counter with active-low reset
module my_counter (
    input  wire clk,      // Clock input
    input  wire rst_n,    // Active-low reset
    output reg [3:0] count // 4-bit counter output
);

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            count <= 4'b0000; // Reset counter to 0
        end else begin
            count <= count + 1; // Increment counter
        end
    end

endmodule
