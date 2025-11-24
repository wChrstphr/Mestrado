// ============================================================
// SCRIPT PARA COLETAR DADOS DO SITE TJDFT
// ============================================================
// 
// INSTRUÇÕES:
// 1. Abra: https://jurisdf.tjdft.jus.br/resultado
// 2. Faça a busca por "fornecimento de medicamento"
// 3. Pressione F12 para abrir DevTools
// 4. Vá na aba "Console"
// 5. Cole este código completo e pressione Enter
// 6. Os dados serão copiados automaticamente
// 7. Cole em um arquivo .txt
// 8. Repita para cada página de resultados
//
// ============================================================

(function() {
    console.log('🔍 Iniciando extração de dados do TJDFT...');
    console.log('📍 URL atual:', window.location.href);
    
    // Tentar diferentes seletores (o site pode usar classes específicas)
    const possiveisSeletores = [
        '.card-resultado',
        '.resultado-item',
        'article',
        'app-resultado-item',
        '[class*="card"]',
        '[class*="resultado"]',
        '[class*="item"]',
        'mat-card',
        '.mat-card'
    ];
    
    let cards = [];
    
    // Tentar cada seletor até encontrar elementos
    for (let seletor of possiveisSeletores) {
        cards = document.querySelectorAll(seletor);
        if (cards.length > 0) {
            console.log(`✅ Encontrados ${cards.length} elementos usando: ${seletor}`);
            break;
        }
    }
    
    // Se não encontrou com seletores, tentar buscar por texto
    if (cards.length === 0) {
        console.log('⚠️  Tentando método alternativo...');
        
        // Buscar todos os elementos que contenham "Processo:" ou "Acórdão"
        const allElements = document.querySelectorAll('*');
        const elementosComProcesso = [];
        
        allElements.forEach(el => {
            const texto = el.innerText || '';
            if ((texto.includes('Processo:') || texto.includes('Acórdão')) && 
                texto.length > 100 && texto.length < 8000) {
                elementosComProcesso.push(el);
            }
        });
        
        // Remover duplicatas (pegar apenas os pais)
        const elementosUnicos = elementosComProcesso.filter((el, index) => {
            // Verificar se não é filho de outro elemento da lista
            return !elementosComProcesso.some((outro, idx) => 
                idx !== index && outro.contains(el)
            );
        });
        
        cards = elementosUnicos;
        console.log(`✅ Encontrados ${cards.length} elementos via busca de texto`);
    }
    
    if (cards.length === 0) {
        console.error('❌ Nenhum resultado encontrado!');
        console.log('💡 Dica: Certifique-se de que a página de resultados está carregada');
        console.log('💡 Aguarde alguns segundos e tente novamente');
        return;
    }
    
    // DEBUG: Mostrar amostra do conteúdo dos cards
    console.log('🔍 DEBUG - Amostra do primeiro card:');
    console.log(cards[0].innerText.substring(0, 200));
    
    // Extrair dados de cada card
    let resultados = [];
    let contador = 0;
    let rejeitados = 0;
    
    cards.forEach((card, index) => {
        try {
            let texto = card.innerText || card.textContent;
            
            // Verificar se tem conteúdo mínimo
            if (!texto || texto.length < 50) {
                return;
            }
            
            const textoLower = texto.toLowerCase();
            
            // MODO MAIS PERMISSIVO: aceitar se tiver qualquer menção a processo judicial
            // Já que a busca foi feita com filtro de "fornecimento medicamento"
            const contemProcesso = textoLower.includes('processo') || 
                                   textoLower.includes('acórdão') ||
                                   texto.match(/\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}/);
            
            if (contemProcesso) {
                resultados.push(texto);
                contador++;
                console.log(`✅ [${contador}] Extraído - ${texto.substring(0, 60)}...`);
            } else {
                rejeitados++;
            }
        } catch (e) {
            console.warn(`⚠️  Erro no card ${index}:`, e);
        }
    });
    
    console.log(`\n📊 Estatísticas:`);
    console.log(`   Total analisado: ${cards.length}`);
    console.log(`   Extraídos: ${contador}`);
    console.log(`   Rejeitados: ${rejeitados}`);
    
    if (resultados.length === 0) {
        console.error('❌ Nenhum resultado relevante encontrado!');
        console.log('\n💡 SOLUÇÃO ALTERNATIVA:');
        console.log('Execute o comando abaixo para extrair TUDO da página:');
        console.log('\ncopy(document.body.innerText);');
        console.log('\nDepois cole em um arquivo .txt');
        return;
    }
    
    // Juntar todos os resultados com separador
    const textoFinal = resultados.join('\n\n===SEPARADOR_PROCESSO===\n\n');
    
    // Tentar copiar para área de transferência
    if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(textoFinal)
            .then(() => {
                console.log('');
                console.log('='.repeat(60));
                console.log('✅ SUCESSO!');
                console.log('='.repeat(60));
                console.log(`📋 ${resultados.length} processos copiados para área de transferência!`);
                console.log('');
                console.log('📝 PRÓXIMOS PASSOS:');
                console.log('1. Cole o conteúdo em um arquivo .txt');
                console.log('2. Navegue para próxima página de resultados');
                console.log('3. Execute este script novamente');
                console.log('4. Cole no FINAL do mesmo arquivo');
                console.log('5. Repita até ter ~500 processos');
                console.log('='.repeat(60));
            })
            .catch(err => {
                console.error('❌ Erro ao copiar:', err);
                console.log('💡 Copie manualmente o texto abaixo:');
                console.log(textoFinal);
            });
    } else {
        // Fallback: mostrar no console
        console.log('');
        console.log('='.repeat(60));
        console.log('📋 DADOS EXTRAÍDOS (copie manualmente):');
        console.log('='.repeat(60));
        console.log(textoFinal);
        console.log('='.repeat(60));
    }
    
    // Retornar dados também como objeto
    return {
        total: resultados.length,
        dados: resultados,
        textoCompleto: textoFinal
    };
    
})();

// ============================================================
// DEPOIS DE COLETAR TODOS OS DADOS:
// ============================================================
// 
// Execute no terminal:
// python extrator_manual_tjdft.py acordaos_tjdft.txt
//
// Isso irá processar o arquivo e gerar um CSV estruturado!
// ============================================================
