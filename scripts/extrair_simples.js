// ============================================================
// SCRIPT SIMPLES - EXTRAÇÃO DIRETA DE TODA A PÁGINA
// ============================================================
// Este script copia TODO o texto visível da página
// Use quando o script principal não funcionar
// ============================================================

(function() {
    console.log('📋 Copiando TODO o conteúdo da página...');
    
    // Pegar todo o texto da página
    const textoCompleto = document.body.innerText;
    
    // Tentar copiar
    if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(textoCompleto)
            .then(() => {
                console.log('✅ SUCESSO!');
                console.log(`📋 ${textoCompleto.length} caracteres copiados!`);
                console.log('\n📝 Próximos passos:');
                console.log('1. Cole em um arquivo .txt');
                console.log('2. Navegue para próxima página');
                console.log('3. Execute novamente');
                console.log('4. Cole NO FINAL do mesmo arquivo');
            })
            .catch(err => {
                console.error('❌ Erro:', err);
            });
    } else {
        // Fallback
        console.log('⚠️  Copie o texto abaixo manualmente:');
        console.log('='.repeat(60));
        console.log(textoCompleto);
        console.log('='.repeat(60));
    }
    
    return textoCompleto;
})();

// ============================================================
// OU AINDA MAIS SIMPLES: Cole apenas este comando no console:
// ============================================================
// 
// copy(document.body.innerText);
//
// Pressione Enter e cole em seu arquivo .txt!
// ============================================================
