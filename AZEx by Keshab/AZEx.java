import java.util.ArrayList;
import java.util.Scanner;

public class AZEx {
    
    static Scanner scanner = new Scanner(System.in);
    static ArrayList<String> transactionHistory = new ArrayList<>();
    static double balance = 0.0;

    public static void main(String[] args) {
        
        System.out.println("╔════════════════════════════════════════╗");
        System.out.println("║     AZEx - A to Z Experiment           ║");
        System.out.println("║     By Keshab Chandra Sahu             ║");
        System.out.println("╚════════════════════════════════════════╝");
        
        while (true) {
            System.out.println("\n┌────────────────────────────────────┐");
            System.out.println("│         MAIN MENU                  │");
            System.out.println("├────────────────────────────────────┤");
            System.out.println("│  1. Money Spending Manager         │");
            System.out.println("│  2. Scientific Calculator          │");
            System.out.println("│  3. Exit                           │");
            System.out.println("└────────────────────────────────────┘");
            System.out.print("\nEnter your choice: ");
            
            int choice = scanner.nextInt();
            
            switch (choice) {
                case 1:
                    moneyManager();
                    break;
                case 2:
                    scientificCalculator();
                    break;
                case 3:
                    System.out.println("\nThank you for using AZEx! Bye!");
                    System.exit(0);
                    break;
                default:
                    System.out.println("\nInvalid choice! Please try again.");
            }
        }
    }
    
    // ==================== MONEY SPENDING MANAGER ====================
    public static void moneyManager() {
        while (true) {
            System.out.println("\n╔════════════════════════════════════════╗");
            System.out.println("║    MONEY SPENDING MANAGER              ║");
            System.out.println("╠════════════════════════════════════════╣");
            System.out.println("║  Current Balance: $" + String.format("%.2f", balance));
            System.out.println("╚════════════════════════════════════════╝");
            
            System.out.println("\n┌────────────────────────────────────┐");
            System.out.println("│  1. Add Income                     │");
            System.out.println("│  2. Add Expense                    │");
            System.out.println("│  3. View Transaction History       │");
            System.out.println("│  4. View Summary                   │");
            System.out.println("│  5. Reset Balance                  │");
            System.out.println("│  6. Back to Main Menu              │");
            System.out.println("└────────────────────────────────────┘");
            System.out.print("\nEnter your choice: ");
            
            int choice = scanner.nextInt();
            
            switch (choice) {
                case 1:
                    addIncome();
                    break;
                case 2:
                    addExpense();
                    break;
                case 3:
                    viewHistory();
                    break;
                case 4:
                    viewSummary();
                    break;
                case 5:
                    resetBalance();
                    break;
                case 6:
                    return;
                default:
                    System.out.println("\nInvalid choice!");
            }
        }
    }
    
    public static void addIncome() {
        System.out.print("\nEnter income amount: $");
        double amount = scanner.nextDouble();
        scanner.nextLine(); // consume newline
        
        System.out.print("Enter description: ");
        String description = scanner.nextLine();
        
        balance += amount;
        transactionHistory.add("+ $" + String.format("%.2f", amount) + " | " + description);
        
        System.out.println("\nIncome added successfully!");
        System.out.println("  New Balance: $" + String.format("%.2f", balance));
    }
    
    public static void addExpense() {
        System.out.print("\nEnter expense amount: $");
        double amount = scanner.nextDouble();
        scanner.nextLine(); // consume newline
        
        if (amount > balance) {
            System.out.println("\nInsufficient balance!");
            System.out.println("  Current Balance: $" + String.format("%.2f", balance));
            return;
        }
        
        System.out.print("Enter description: ");
        String description = scanner.nextLine();
        
        balance -= amount;
        transactionHistory.add("- $" + String.format("%.2f", amount) + " | " + description);
        
        System.out.println("\nExpense recorded successfully!");
        System.out.println("  Remaining Balance: $" + String.format("%.2f", balance));
    }
    
    public static void viewHistory() {
        if (transactionHistory.isEmpty()) {
            System.out.println("\nNo transactions yet!");
            return;
        }
        
        System.out.println("\n╔════════════════════════════════════════╗");
        System.out.println("║      TRANSACTION HISTORY               ║");
        System.out.println("╚════════════════════════════════════════╝");
        
        for (int i = 0; i < transactionHistory.size(); i++) {
            System.out.println((i + 1) + ". " + transactionHistory.get(i));
        }
    }
    
    public static void viewSummary() {
        double totalIncome = 0;
        double totalExpense = 0;
        
        for (String transaction : transactionHistory) {
            if (transaction.startsWith("+")) {
                String[] parts = transaction.split(" ");
                totalIncome += Double.parseDouble(parts[1].substring(1));
            } else if (transaction.startsWith("-")) {
                String[] parts = transaction.split(" ");
                totalExpense += Double.parseDouble(parts[1].substring(1));
            }
        }
        
        System.out.println("\n╔════════════════════════════════════════╗");
        System.out.println("║         FINANCIAL SUMMARY              ║");
        System.out.println("╠════════════════════════════════════════╣");
        System.out.println("║  Total Income:  $" + String.format("%.2f", totalIncome));
        System.out.println("║  Total Expense: $" + String.format("%.2f", totalExpense));
        System.out.println("║  Current Balance: $" + String.format("%.2f", balance));
        System.out.println("║  Transactions: " + transactionHistory.size());
        System.out.println("╚════════════════════════════════════════╝");
    }
    
    public static void resetBalance() {
        System.out.print("\nAre you sure you want to reset? (y/n): ");
        char confirm = scanner.next().charAt(0);
        
        if (confirm == 'y' || confirm == 'Y') {
            balance = 0.0;
            transactionHistory.clear();
            System.out.println("\nBalance reset successfully!");
        } else {
            System.out.println("\nReset cancelled.");
        }
    }
    
    // ==================== SCIENTIFIC CALCULATOR ====================
    public static void scientificCalculator() {
        while (true) {
            System.out.println("\n╔════════════════════════════════════════╗");
            System.out.println("║      SCIENTIFIC CALCULATOR             ║");
            System.out.println("╚════════════════════════════════════════╝");
            
            System.out.println("\n┌────────────────────────────────────┐");
            System.out.println("│  BASIC OPERATIONS                  │");
            System.out.println("│  1. Addition          (+)          │");
            System.out.println("│  2. Subtraction       (-)          │");
            System.out.println("│  3. Multiplication    (*)          │");
            System.out.println("│  4. Division          (÷)          │");
            System.out.println("│                                    │");
            System.out.println("│  ADVANCED OPERATIONS               │");
            System.out.println("│  5. Power             (x^y)        │");
            System.out.println("│  6. Square Root       (√)          │");
            System.out.println("│  7. Logarithm         (log)        │");
            System.out.println("│  8. Natural Log       (ln)         │");
            System.out.println("│                                    │");
            System.out.println("│  TRIGONOMETRIC FUNCTIONS           │");
            System.out.println("│  9. Sine              (sin)        │");
            System.out.println("│  10. Cosine           (cos)        │");
            System.out.println("│  11. Tangent          (tan)        │");
            System.out.println("│                                    │");
            System.out.println("│  12. Factorial        (n!)         │");
            System.out.println("│  13. Back to Main Menu             │");
            System.out.println("└────────────────────────────────────┘");
            System.out.print("\nEnter your choice: ");
            
            int choice = scanner.nextInt();
            
            if (choice == 13) {
                return;
            }
            
            performCalculation(choice);
        }
    }
    
    public static void performCalculation(int choice) {
        double num1, num2, result = 0;
        
        switch (choice) {
            case 1: // Addition
                System.out.print("\nEnter first number: ");
                num1 = scanner.nextDouble();
                System.out.print("Enter second number: ");
                num2 = scanner.nextDouble();
                result = num1 + num2;
                System.out.println("\nResult: " + num1 + " + " + num2 + " = " + result);
                break;
                
            case 2: // Subtraction
                System.out.print("\nEnter first number: ");
                num1 = scanner.nextDouble();
                System.out.print("Enter second number: ");
                num2 = scanner.nextDouble();
                result = num1 - num2;
                System.out.println("\nResult: " + num1 + " - " + num2 + " = " + result);
                break;
                
            case 3: // Multiplication
                System.out.print("\nEnter first number: ");
                num1 = scanner.nextDouble();
                System.out.print("Enter second number: ");
                num2 = scanner.nextDouble();
                result = num1 * num2;
                System.out.println("\nResult: " + num1 + " * " + num2 + " = " + result);
                break;
                
            case 4: // Division
                System.out.print("\nEnter numerator: ");
                num1 = scanner.nextDouble();
                System.out.print("Enter denominator: ");
                num2 = scanner.nextDouble();
                if (num2 == 0) {
                    System.out.println("\nError: Division by zero!");
                } else {
                    result = num1 / num2;
                    System.out.println("\nResult: " + num1 + " ÷ " + num2 + " = " + result);
                }
                break;
                
            case 5: // Power
                System.out.print("\nEnter base: ");
                num1 = scanner.nextDouble();
                System.out.print("Enter exponent: ");
                num2 = scanner.nextDouble();
                result = Math.pow(num1, num2);
                System.out.println("\nResult: " + num1 + "^" + num2 + " = " + result);
                break;
                
            case 6: // Square Root
                System.out.print("\nEnter number: ");
                num1 = scanner.nextDouble();
                if (num1 < 0) {
                    System.out.println("\nError: Cannot calculate square root of negative number!");
                } else {
                    result = Math.sqrt(num1);
                    System.out.println("\nResult: √" + num1 + " = " + result);
                }
                break;
                
            case 7: // Logarithm (base 10)
                System.out.print("\nEnter number: ");
                num1 = scanner.nextDouble();
                if (num1 <= 0) {
                    System.out.println("\nError: Logarithm undefined for non-positive numbers!");
                } else {
                    result = Math.log10(num1);
                    System.out.println("\nResult: log(" + num1 + ") = " + result);
                }
                break;
                
            case 8: // Natural Logarithm
                System.out.print("\nEnter number: ");
                num1 = scanner.nextDouble();
                if (num1 <= 0) {
                    System.out.println("\nError: Natural logarithm undefined for non-positive numbers!");
                } else {
                    result = Math.log(num1);
                    System.out.println("\nResult: ln(" + num1 + ") = " + result);
                }
                break;
                
            case 9: // Sine
                System.out.print("\nEnter angle in degrees: ");
                num1 = scanner.nextDouble();
                result = Math.sin(Math.toRadians(num1));
                System.out.println("\nResult: sin(" + num1 + "°) = " + result);
                break;
                
            case 10: // Cosine
                System.out.print("\nEnter angle in degrees: ");
                num1 = scanner.nextDouble();
                result = Math.cos(Math.toRadians(num1));
                System.out.println("\nResult: cos(" + num1 + "°) = " + result);
                break;
                
            case 11: // Tangent
                System.out.print("\nEnter angle in degrees: ");
                num1 = scanner.nextDouble();
                result = Math.tan(Math.toRadians(num1));
                System.out.println("\nResult: tan(" + num1 + "°) = " + result);
                break;
                
            case 12: // Factorial
                System.out.print("\nEnter a non-negative integer: ");
                int n = scanner.nextInt();
                if (n < 0) {
                    System.out.println("\nError: Factorial not defined for negative numbers!");
                } else {
                    long factorial = 1;
                    for (int i = 1; i <= n; i++) {
                        factorial *= i;
                    }
                    System.out.println("\nResult: " + n + "! = " + factorial);
                }
                break;
                
            default:
                System.out.println("\nInvalid choice!");
        }
    }
}